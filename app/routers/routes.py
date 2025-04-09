import re
import traceback

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException

from app.services.email_service import send_contact_info_email
from app.database.repository import search_similar_knowledge, save_knowledge_record
from app.services.chat_memory import get_history, add_to_history
from app.core.dependencies import get_db_session, get_gpt_service, get_redis_client
from app.services.language_detection import detect_language_with_fallback


router = APIRouter()


class AskRequest(BaseModel):
    message: str
    chat_id: str


class AskResponse(BaseModel):
    response: str


@router.get("/", response_model=dict)
async def root():
    return {"message": "API is running"}


def contains_contact_info(text: str) -> bool:
    email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    phone_pattern = r"(?<!\d)(\+?7|8|\+375|\+380)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}(?!\d)"
    return bool(re.search(email_pattern, text) or re.search(phone_pattern, text))


@router.post("/ask", response_model=AskResponse)
async def ask(
    data: AskRequest,
    gpt=Depends(get_gpt_service),
    redis=Depends(get_redis_client),
    db: AsyncSession = Depends(get_db_session),
):
    user_message = data.message.strip()
    chat_id = data.chat_id.strip()

    current_lang = await redis.get(f"chat_language:{chat_id}")

    new_lang = detect_language_with_fallback(user_message, current_lang)

    await redis.set(f"chat_language:{chat_id}", new_lang)
    await add_to_history(chat_id, "user", user_message, redis)
    
    
    history = await get_history(chat_id, redis)
    user_embedding = await gpt.get_embedding(user_message)
    similar_records = await search_similar_knowledge(user_embedding, db, limit=3)
    context = "\n\n".join(
        f"Q: {row['question']}\nA: {row['answer']}"
        for row in similar_records
    ) if similar_records else ""

    response_text = await gpt.generate_gpt_response(
        history,
        context=context,
        lang=new_lang
    )

    await add_to_history(chat_id, "assistant", response_text, redis)
    
    try:
        await save_knowledge_record(user_message, response_text, db, gpt)
    except Exception:
        traceback.print_exc()

    if contains_contact_info(user_message):
        recent_messages = history[-10:]
        try:
            await send_contact_info_email(chat_id, recent_messages)
        except Exception:
            traceback.print_exc()

    return {"response": response_text}
