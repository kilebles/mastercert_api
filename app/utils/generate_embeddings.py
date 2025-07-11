import asyncio
import logging

from sqlalchemy import select
from openai import AsyncOpenAI

from app.database.db import SessionLocal
from app.database.models import KnowledgeBase
from app.core.settings import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)

async def generate_embeddings():
    async with SessionLocal() as session:
        result = await session.execute(
            select(KnowledgeBase).where(KnowledgeBase.embedding.is_(None))
        )
        records = result.scalars().all()

        for record in records:
            content = f"{record.question.strip()} {record.answer.strip()}"
            try:
                response = await client.embeddings.create(
                    input=content,
                    model="text-embedding-3-small",
                    encoding_format="float"
                )
                record.embedding = response.data[0].embedding
                logger.info(f"Embedding generated for id={record.id}")
            except Exception as e:
                logger.error(f"Error for id={record.id}: {e}")

        await session.commit()
        logger.info("Embeddings generation completed")

if __name__ == "__main__":
    asyncio.run(generate_embeddings())