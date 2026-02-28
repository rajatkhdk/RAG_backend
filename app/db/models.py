from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class DocumentChunk(Base):
    __tablename__ = "Document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    chunk_index = Column(Integer)
    chunk_text = Column(Text)
    strategy = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)