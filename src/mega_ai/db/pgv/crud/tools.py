from __future__ import annotations

from sqlalchemy.orm import Session

from mega_ai.db.pgv.models import ToolCall
from mega_ai.db.pgv.schemas.tools import ToolCallCreate


# --- CREATE ---
def create_tool_call(db: Session, obj_in: ToolCallCreate) -> ToolCall:
    db_obj = ToolCall(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


# --- LIST ---
def list_tool_calls_for_job(db: Session, job_id: str) -> list[ToolCall]:
    return (
        db.query(ToolCall)
        .filter(ToolCall.job_id == job_id)
        .order_by(ToolCall.created_at.asc(), ToolCall.retry_number.asc())
        .all()
    )
