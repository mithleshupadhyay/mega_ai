from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from mega_ai.db.pgv.db import get_db
from mega_ai.service.trace_service import TraceService

router = APIRouter(prefix="/v1/jobs", tags=["jobs"])


@router.get("/{job_id}/trace")
def get_job_trace(job_id: str, db: Session = Depends(get_db)) -> dict[str, object]:
    trace = TraceService(db).get_trace(job_id)
    if trace is None:
        raise HTTPException(status_code=404, detail="Job trace was not found.")
    return trace
