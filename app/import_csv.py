import asyncio
import csv
import logging

from app.database.db import SessionLocal
from app.database.models import KnowledgeBase
from sqlalchemy import select

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def load_csv_to_db():
    async with SessionLocal() as session:
        with open("app/data.csv", newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)

            for row in reader:
                if len(row) < 2:
                    continue

                question = row[0].strip().strip('"')
                answer = row[1].strip().strip('"')
                url = row[2].strip().strip('"') if len(row) > 2 else None

                if url and (url.lower() == "none" or url == ""):
                    url = None

                result = await session.execute(
                    select(KnowledgeBase).where(KnowledgeBase.question == question)
                )
                if result.scalar():
                    continue

                entry = KnowledgeBase(
                    question=question,
                    answer=answer,
                    url=url
                )
                session.add(entry)

            await session.commit()
            logger.info("CSV was imported successfully")

if __name__ == "__main__":
    asyncio.run(load_csv_to_db())
