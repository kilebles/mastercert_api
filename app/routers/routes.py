import traceback

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException

from app.database.repository import search_similar_knowledge
from app.services.chat_memory import get_history, add_to_history
from app.core.dependencies import get_db_session, get_gpt_service, get_redis_client

router = APIRouter()

class AskRequest(BaseModel):
    message: str
    chat_id: str


class AskResponse(BaseModel):
    response: str


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
    await add_to_history(chat_id, "user", user_message, redis)

    history = await get_history(chat_id, redis)

    user_embedding = await gpt.get_embedding(user_message)
    similar_records = await search_similar_knowledge(user_embedding, db, limit=3)
    context = "\n\n".join(
        f"Q: {row['question']}\nA: {row['answer']}"
        for row in similar_records
    ) if similar_records else ""

    response_text = await gpt.generate_gpt_response(history, context=context)

    await add_to_history(chat_id, "assistant", response_text, redis)
    
    return {"response": response_text}