from __future__ import annotations

from mega_ai.core.logging.structured import utc_now
from mega_ai.db.pgv.schemas.jobs import JobCreate


def test_job_create_schema_keeps_service_style_fields() -> None:
    now = utc_now()
    data = JobCreate(id="job-schema", status="running", query="hello", created_at=now, updated_at=now)

    assert data.id == "job-schema"
    assert data.status == "running"
    assert data.created_at == now
