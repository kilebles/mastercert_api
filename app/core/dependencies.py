from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_db
from app.services.gpt_service import openai_service


async def get_db_session(db: AsyncSession = Depends(get_db)):
    return db


async def get_gpt_service():
    return openai_service