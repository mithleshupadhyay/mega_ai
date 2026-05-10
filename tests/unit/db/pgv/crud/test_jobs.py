from __future__ import annotations

from mega_ai.core.logging.structured import utc_now
from mega_ai.db.pgv.crud.jobs import create_job, get_job, mark_job_completed
from mega_ai.db.pgv.schemas.jobs import JobCreate


def test_create_and_complete_job(db_session) -> None:
    now = utc_now()
    job = create_job(
        db_session,
        JobCreate(id="job-crud", status="running", query="hello", created_at=now, updated_at=now),
    )

    completed = mark_job_completed(
        db_session,
        job,
        final_answer="done",
        provenance_map={"sentences": []},
        updated_at=utc_now(),
    )
    fetched = get_job(db_session, "job-crud")

    assert completed.status == "completed"
    assert fetched is not None
    assert fetched.final_answer == "done"
