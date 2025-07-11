from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.database.db import get_db
from app.core.settings import config
from app.services.gpt_service import openai_service


async def get_db_session(db: AsyncSession = Depends(get_db)) -> AsyncSession:
    return db


async def get_gpt_service():
    return openai_service


_redis_instance: Redis | None = None


async def get_redis_client() -> Redis:
    global _redis_instance
    if _redis_instance is None:
        _redis_instance = Redis(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            decode_responses=True,
        )
    return _redis_instance
