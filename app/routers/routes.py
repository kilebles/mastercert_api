from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException

from app.database.repository import search_similar_knowledge
from app.core.dependencies import get_db_session, get_gpt_service

router = APIRouter()


class AskRequest(BaseModel):
    message: str


class AskResponse(BaseModel):
    response: str


@router.get("/", response_model=dict)
async def root():
    return {"message": "API is running"}


@router.post("/ask", response_model=AskResponse)
async def ask(
    data: AskRequest,
    gpt=Depends(get_gpt_service),
    db: AsyncSession = Depends(get_db_session),
):
    user_message = data.message

    try:
        user_embedding = await gpt.get_embedding(user_message)
        similar_records = await search_similar_knowledge(user_embedding, db, limit=3)
        context = "\n\n".join(
            f"Q: {row['question']}\nA: {row['answer']}" for row in similar_records
        ) if similar_records else ""
        response = await gpt.generate_gpt_response(user_message, context=context)

        return {"response": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GPT error: {e}")