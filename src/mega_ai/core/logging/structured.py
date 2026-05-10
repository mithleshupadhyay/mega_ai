from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from mega_ai.core.logging.redaction import stable_hash
from mega_ai.db.pgv.crud.traces import create_trace_event, get_next_event_order
from mega_ai.db.pgv.models import TraceEvent
from mega_ai.db.pgv.schemas.jobs import TraceEventCreate


def utc_now() -> datetime:
    return datetime.now(UTC)


def emit_trace(
    db: Session,
    *,
    job_id: str,
    event_type: str,
    agent_id: str | None = None,
    payload: dict[str, object] | None = None,
    input_text: str | None = None,
    output_text: str | None = None,
    latency_ms: int | None = None,
    token_count: int | None = None,
    policy_violations: list[str] | None = None,
) -> TraceEvent:
    return create_trace_event(
        db,
        TraceEventCreate(
            job_id=job_id,
            event_order=get_next_event_order(db, job_id),
            timestamp=utc_now(),
            agent_id=agent_id,
            event_type=event_type,
            input_hash=stable_hash(input_text),
            output_hash=stable_hash(output_text),
            latency_ms=latency_ms,
            token_count=token_count,
            policy_violations=policy_violations or [],
            payload=payload or {},
        ),
    )
