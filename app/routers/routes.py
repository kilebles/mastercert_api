import logging
import traceback

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends

from app.database.repository import search_similar_knowledge, save_knowledge_record
from app.services.chat_memory import clear_history, get_history, add_to_history
from app.core.dependencies import get_db_session, get_gpt_service, get_redis_client

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

router = APIRouter()


class AskRequest(BaseModel):
    message: str
    chat_id: str


class AskResponse(BaseModel):
    response: str
    
    
class ClearRequest(BaseModel):
    chat_id: str


@router.get("/", response_model=dict)
async def root():
    return {"message": "API is running"}


@router.post("/ask", response_model=AskResponse)
async def ask(
    data: AskRequest,
    gpt=Depends(get_gpt_service),
    redis=Depends(get_redis_client),
    db: AsyncSession = Depends(get_db_session),
):
    user_message = data.message.strip()
    chat_id = data.chat_id.strip()

    history = await get_history(chat_id, redis, limit=10)
    history.append({"role": "user", "content": user_message})

    user_embedding = await gpt.get_embedding(user_message)
    similar_records = await search_similar_knowledge(user_embedding, db, limit=3)

    context = "\n\n".join(
        f"Q: {row['question']}\nA: {row['answer']}"
        for row in similar_records
    ) if similar_records else ""

    logger.warning("=== REDIS HISTORY BEFORE ===")
    for m in await get_history(chat_id, redis, limit=10):
        logger.warning(f"{m['role']}: {m['content']}")

    logger.warning("=== FINAL HISTORY SENT TO GPT ===")
    for m in history:
        logger.warning(f"{m['role']}: {m['content']}")

    logger.warning("=== CONTEXT FROM EMBEDDING ===")
    logger.warning(context)

    response_text = await gpt.generate_gpt_response(
        history,
        context=context,
    )

    logger.warning("=== GPT RESPONSE ===")
    logger.warning(response_text)

    await add_to_history(chat_id, "user", user_message, redis)
    await add_to_history(chat_id, "assistant", response_text, redis)

    return {"response": response_text}


@router.post("/clear")
async def clear_chat(data: ClearRequest, redis=Depends(get_redis_client)):
    logger.info(f"Clearing Redis history for chat_id={data.chat_id}")
    await clear_history(data.chat_id, redis)
    return {"status": "ok"}