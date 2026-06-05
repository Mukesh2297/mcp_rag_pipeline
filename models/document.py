from db import Base
from sqlalchemy import Column, DateTime, Integer, Text, JSON
from sqlalchemy.dialects.postgresql import TSVECTOR
from pgvector.sqlalchemy import Vector

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(768), nullable=False)
    tsv = Column(TSVECTOR, nullable=True)
