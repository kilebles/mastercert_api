from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.services import openai_service
from app.core.dependensies import get_db_session, get_gpt_service

router = APIRouter()


class AskRequest(BaseModel):
    message: str
    

class AskResponse(BaseModel):
    response: str


@router.get("/", response_model=dict)
async def root():
    return {"message": "API is running"}


@router.post("/ask", response_model=AskResponse)
async def ask(data: AskRequest, gpt=Depends(get_gpt_service), db=Depends(get_db_session)):
    user_message = data.message
    try:
        gpt_reply = await openai_service.generate_gpt_response(user_message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"response": gpt_reply}