from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from mega_ai.api.schemas import PromptRewriteDecisionRequest
from mega_ai.db.pgv.db import get_db
from mega_ai.service.prompt_rewrite_service import PromptRewriteService

router = APIRouter(prefix="/v1/prompts", tags=["prompts"])


@router.post("/rewrites/{rewrite_id}/decision")
def decide_prompt_rewrite(
    rewrite_id: str,
    request: PromptRewriteDecisionRequest,
    db: Session = Depends(get_db),
) -> dict[str, object]:
    result = PromptRewriteService(db).decide(
        rewrite_id=rewrite_id,
        decision=request.decision,
        reviewer_note=request.reviewer_note,
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Prompt rewrite proposal was not found.")
    return result
