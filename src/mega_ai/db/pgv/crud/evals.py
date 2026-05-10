from __future__ import annotations

from sqlalchemy.orm import Session

from mega_ai.db.pgv.models import EvalCaseResult, EvalRun
from mega_ai.db.pgv.schemas.evals import EvalCaseResultCreate, EvalRunCreate, EvalRunUpdate


# --- CREATE ---
def create_eval_run(db: Session, obj_in: EvalRunCreate) -> EvalRun:
    db_obj = EvalRun(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def create_eval_case_result(db: Session, obj_in: EvalCaseResultCreate) -> EvalCaseResult:
    db_obj = EvalCaseResult(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


# --- GET ---
def get_eval_run(db: Session, eval_run_id: str) -> EvalRun | None:
    return db.get(EvalRun, eval_run_id)


def get_latest_eval_run(db: Session) -> EvalRun | None:
    return db.query(EvalRun).order_by(EvalRun.started_at.desc()).first()


# --- LIST ---
def list_failed_case_results(db: Session, eval_run_id: str) -> list[EvalCaseResult]:
    return (
        db.query(EvalCaseResult)
        .filter(EvalCaseResult.eval_run_id == eval_run_id, EvalCaseResult.passed.is_(False))
        .all()
    )


# --- UPDATE ---
def update_eval_run(db: Session, db_obj: EvalRun, obj_in: EvalRunUpdate) -> EvalRun:
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj
