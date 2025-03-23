from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_db
from app.services.gpt_service import openai_service
from app.services.redis_client import redis_client


async def get_db_session(db: AsyncSession = Depends(get_db)):
    return db


async def get_gpt_service():
    return openai_service


async def get_redis_client():
    return redis_client