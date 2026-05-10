from sqlalchemy import Column, Integer, String, Text, UniqueConstraint

from mega_ai.db.pgv import db as pgv_db
from mega_ai.db.pgv.models.types import json_type

Base = pgv_db.Base


class RetrievedChunk(Base):
    __tablename__ = "retrieved_chunks"
    __table_args__ = (UniqueConstraint("chunk_id", name="uq_chunk_id"),)

    chunk_id = Column(String(80), primary_key=True)
    title = Column(String(200))
    content = Column(Text)
    source_url = Column(Text)
    tags = Column(json_type(), default=list)


class StructuredRecord(Base):
    __tablename__ = "structured_records"
    __table_args__ = (UniqueConstraint("record_key", name="uq_record_key"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    record_key = Column(String(120), index=True)
    category = Column(String(80), index=True)
    value = Column(Text)
    metadata_json = Column(json_type(), default=dict)
