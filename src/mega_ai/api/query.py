from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from mega_ai.api.schemas import QueryRequest
from mega_ai.db.pgv.db import get_db
from mega_ai.service.job_service import JobService

router = APIRouter(prefix="/v1/query", tags=["query"])


@router.post("/stream")
def submit_query_stream(request: QueryRequest, db: Session = Depends(get_db)) -> StreamingResponse:
    generator = JobService(db).run_query_stream(request.query)
    return StreamingResponse(generator, media_type="text/event-stream")
