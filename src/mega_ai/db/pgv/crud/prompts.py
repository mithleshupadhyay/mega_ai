from __future__ import annotations

from sqlalchemy.orm import Session

from mega_ai.agents.prompts import DEFAULT_PROMPTS, prompt_id
from mega_ai.db.pgv.models import PerformanceDelta, PromptRewriteProposal, PromptVersion
from mega_ai.db.pgv.schemas.prompts import (
    PerformanceDeltaCreate,
    PromptRewriteProposalCreate,
    PromptVersionCreate,
)


def get_active_prompt(db: Session, agent_id: str) -> PromptVersion:
    prompt = (
        db.query(PromptVersion)
        .filter(PromptVersion.agent_id == agent_id, PromptVersion.is_active.is_(True))
        .order_by(PromptVersion.version.desc())
        .first()
    )
    if prompt is not None:
        return prompt
    return PromptVersion(
        id=prompt_id(agent_id),
        agent_id=agent_id,
        version=1,
        prompt_text=DEFAULT_PROMPTS[agent_id],
        is_active=True,
    )


def active_prompt_snapshot(db: Session) -> dict[str, str]:
    rows = db.query(PromptVersion).filter(PromptVersion.is_active.is_(True)).all()
    return {row.agent_id: row.id for row in rows}


# --- CREATE ---
def create_prompt_version(db: Session, obj_in: PromptVersionCreate) -> PromptVersion:
    db_obj = PromptVersion(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def create_prompt_rewrite_proposal(
    db: Session, obj_in: PromptRewriteProposalCreate
) -> PromptRewriteProposal:
    db_obj = PromptRewriteProposal(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def create_performance_delta(db: Session, obj_in: PerformanceDeltaCreate) -> PerformanceDelta:
    db_obj = PerformanceDelta(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


# --- GET ---
def get_prompt_rewrite_proposal(db: Session, rewrite_id: str) -> PromptRewriteProposal | None:
    return db.get(PromptRewriteProposal, rewrite_id)


def get_latest_approved_rewrite(db: Session) -> PromptRewriteProposal | None:
    return (
        db.query(PromptRewriteProposal)
        .filter(PromptRewriteProposal.status == "approved")
        .order_by(PromptRewriteProposal.decided_at.desc())
        .first()
    )


# --- LIST ---
def list_rewrite_proposals_for_eval(db: Session, eval_run_id: str) -> list[PromptRewriteProposal]:
    return (
        db.query(PromptRewriteProposal)
        .filter_by(eval_run_id=eval_run_id)
        .order_by(PromptRewriteProposal.created_at.desc())
        .all()
    )
