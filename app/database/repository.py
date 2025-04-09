from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import KnowledgeBase
from app.services.gpt_service import OpenAIService


async def search_similar_knowledge(user_embedding: list[float], session: AsyncSession, limit: int = 3):
    embedding_str = ','.join(map(str, user_embedding))
    
    query = text(f"""
        SELECT * FROM knowledge_base
        ORDER BY embedding <-> '[{embedding_str}]'
        LIMIT :limit
    """)

    result = await session.execute(query, {"limit": limit})
    return result.mappings().all()


async def save_knowledge_recor(
    question: str,
    answer: str,
    session: AsyncSession,
    gpt: OpenAIService,
    url: str = None
) -> None:
    text_to_embed = f"{question.strip()} {answer.strip()}"
    embedding = await gpt.get_embedding(text_to_embed)
    
    record = KnowledgeBase(
        question=question,
        answer=answer,
        url=url,
        embedding=embedding,
    )
    session.add(record)
    await session.commit()