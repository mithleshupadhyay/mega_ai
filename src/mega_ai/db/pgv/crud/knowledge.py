from __future__ import annotations

from sqlalchemy.orm import Session

from mega_ai.db.pgv.models import RetrievedChunk, StructuredRecord
from mega_ai.db.pgv.schemas.knowledge import RetrievedChunkCreate, StructuredRecordCreate


# --- CREATE ---
def create_retrieved_chunk(db: Session, obj_in: RetrievedChunkCreate) -> RetrievedChunk:
    db_obj = RetrievedChunk(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def create_structured_record(db: Session, obj_in: StructuredRecordCreate) -> StructuredRecord:
    db_obj = StructuredRecord(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


# --- GET ---
def get_retrieved_chunk(db: Session, chunk_id: str) -> RetrievedChunk | None:
    return db.get(RetrievedChunk, chunk_id)


def get_structured_record(db: Session, record_key: str) -> StructuredRecord | None:
    return (
        db.query(StructuredRecord)
        .filter(StructuredRecord.record_key == record_key)
        .one_or_none()
    )


# --- LIST ---
def list_retrieved_chunks(db: Session) -> list[RetrievedChunk]:
    return db.query(RetrievedChunk).all()
