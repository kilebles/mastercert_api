from sqlalchemy import Column, Integer, String, Text
from pgvector.sqlalchemy import Vector

from app.database.db import Base


class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"
    
    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    url = Column(String, nullable=True)
    embedding = Column(Vector(1536), nullable=True)