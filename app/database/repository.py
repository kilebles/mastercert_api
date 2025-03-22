from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import KnowledgeBase

async def search_similar_knowledge(user_embedding: list[float], session: AsyncSession, limit: int = 3):
    embedding_str = ','.join(map(str, user_embedding))
    
    query = text(f"""
        SELECT * FROM knowledge_base
        ORDER BY embedding <-> '[{embedding_str}]'
        LIMIT :limit
    """)

    result = await session.execute(query, {"limit": limit})
    return result.mappings().all()
