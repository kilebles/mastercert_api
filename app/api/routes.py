from fastapi import APIRouter

from app.services import openai_service

router = APIRouter()


@router.get("/")
async def root():
    return {"message": "API is running"}


@router.post("/ask")
async def ask(data: dict):
    user_message = data.get("message", "Nothing")
    gpt_reply = await openai_service.generate_gpt_response(user_message)
    return {"response": gpt_reply}