from __future__ import annotations

from sqlalchemy.orm import Session

from mega_ai.db.pgv.models import AgentExecution, Job
from mega_ai.db.pgv.schemas.jobs import AgentExecutionCreate, JobCreate, JobUpdate


# --- CREATE ---
def create_job(db: Session, obj_in: JobCreate) -> Job:
    db_obj = Job(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def create_agent_execution(db: Session, obj_in: AgentExecutionCreate) -> AgentExecution:
    db_obj = AgentExecution(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


# --- GET ONE ---
def get_job(db: Session, job_id: str) -> Job | None:
    return db.get(Job, job_id)


# --- UPDATE ---
def update_job(db: Session, db_obj: Job, obj_in: JobUpdate) -> Job:
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def mark_job_completed(
    db: Session,
    db_obj: Job,
    *,
    final_answer: str | None,
    provenance_map: dict[str, object],
    updated_at,
) -> Job:
    return update_job(
        db,
        db_obj,
        JobUpdate(
            status="completed",
            final_answer=final_answer,
            provenance_map=provenance_map,
            updated_at=updated_at,
        ),
    )


def mark_job_failed(db: Session, db_obj: Job, *, error_code: str, updated_at) -> Job:
    return update_job(
        db,
        db_obj,
        JobUpdate(status="failed", error_code=error_code, updated_at=updated_at),
    )
