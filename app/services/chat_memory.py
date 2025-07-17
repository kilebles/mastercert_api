import json

from typing import List, Dict
from redis.asyncio import Redis

MAX_HISTORY_MESSAGES = 20


def _get_redis_key(chat_id: str) -> str:
    return f"chat_history:{chat_id}"


async def add_to_history(chat_id: str, role: str, content: str, redis: Redis) -> None:
    key = _get_redis_key(chat_id)
    entry = json.dumps({"role": role, "content": content})
    await redis.rpush(key, entry)
    await redis.ltrim(key, 0, MAX_HISTORY_MESSAGES - 1)


async def get_history(chat_id: str, redis: Redis, limit: int = 10) -> List[Dict]:
    key = _get_redis_key(chat_id)
    entries = await redis.lrange(key, -limit * 2, -1)
    return [json.loads(entry) for entry in entries]


async def clear_history(chat_id: str, redis: Redis):
    key = _get_redis_key(chat_id)
    await redis.delete(key)