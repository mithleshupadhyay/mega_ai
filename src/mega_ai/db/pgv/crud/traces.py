from __future__ import annotations

from sqlalchemy.orm import Session

from mega_ai.db.pgv.models import TraceEvent
from mega_ai.db.pgv.schemas.jobs import TraceEventCreate


# --- CREATE ---
def create_trace_event(db: Session, obj_in: TraceEventCreate) -> TraceEvent:
    db_obj = TraceEvent(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


# --- GET ---
def get_next_event_order(db: Session, job_id: str) -> int:
    latest_order = (
        db.query(TraceEvent.event_order)
        .filter(TraceEvent.job_id == job_id)
        .order_by(TraceEvent.event_order.desc())
        .limit(1)
        .scalar()
    )
    return 0 if latest_order is None else int(latest_order) + 1


def list_trace_events(db: Session, job_id: str) -> list[TraceEvent]:
    return (
        db.query(TraceEvent)
        .filter(TraceEvent.job_id == job_id)
        .order_by(TraceEvent.event_order.asc())
        .all()
    )
