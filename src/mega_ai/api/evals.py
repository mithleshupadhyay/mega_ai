from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from mega_ai.api.schemas import TargetedRerunRequest
from mega_ai.db.pgv.db import get_db
from mega_ai.service.eval_service import EvalService

router = APIRouter(prefix="/v1/evals", tags=["evals"])


@router.get("/latest")
def get_latest_eval(db: Session = Depends(get_db)) -> dict[str, object]:
    return EvalService(db).latest_or_run()


@router.post("/targeted-rerun")
def trigger_targeted_rerun(
    request: TargetedRerunRequest,
    db: Session = Depends(get_db),
) -> dict[str, object]:
    return EvalService(db).run_targeted_failed_cases(request.eval_run_id)
