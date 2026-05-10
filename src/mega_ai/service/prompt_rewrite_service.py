from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from mega_ai.core.logging.structured import utc_now
from mega_ai.db.pgv.crud.prompts import (
    create_prompt_rewrite_proposal,
    create_prompt_version,
    get_active_prompt,
    get_latest_approved_rewrite,
    get_prompt_rewrite_proposal,
)
from mega_ai.db.pgv.models import PromptRewriteProposal
from mega_ai.db.pgv.schemas.prompts import PromptRewriteProposalCreate, PromptVersionCreate


class PromptRewriteService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def propose_from_eval(
        self,
        *,
        eval_run_id: str,
        summary: dict[str, object],
        worst_dimension: str,
        target_agent: str,
    ) -> PromptRewriteProposal:
        old = get_active_prompt(self.db, target_agent)
        rewrite_id = f"rewrite-{uuid.uuid4().hex[:12]}"
        new_prompt = (
            old.prompt_text
            + " Before producing output, verify required evidence, reject unsupported claims, "
            "and explain fallback behavior for the weakest scoring dimension."
        )
        return create_prompt_rewrite_proposal(
            self.db,
            PromptRewriteProposalCreate(
                id=rewrite_id,
                eval_run_id=eval_run_id,
                agent_id=target_agent,
                target_dimension=worst_dimension,
                old_prompt=old.prompt_text,
                new_prompt=new_prompt,
                structured_diff={
                    "operation": "append_instruction",
                    "added": (
                        "verify required evidence, reject unsupported claims, and explain fallback behavior"
                    ),
                    "summary_score": summary.get("average_total_score"),
                },
                justification=(
                    f"The latest eval summary shows {worst_dimension} as the weakest dimension. "
                    "The rewrite makes acceptance criteria explicit while keeping human approval required."
                ),
                status="pending",
                created_at=utc_now(),
            ),
        )

    def decide(self, rewrite_id: str, decision: str, reviewer_note: str) -> dict[str, object] | None:
        proposal = get_prompt_rewrite_proposal(self.db, rewrite_id)
        if proposal is None:
            return None
        if proposal.status != "pending":
            return {
                "rewrite_id": rewrite_id,
                "status": proposal.status,
                "message": "Rewrite already decided.",
            }
        proposal.status = "approved" if decision == "approve" else "rejected"
        proposal.reviewer_note = reviewer_note
        proposal.decided_at = utc_now()
        approved_prompt_id = None
        if decision == "approve":
            active = get_active_prompt(self.db, proposal.agent_id)
            active.is_active = False
            new_version = active.version + 1
            approved_prompt_id = f"{proposal.agent_id}-v{new_version}"
            create_prompt_version(
                self.db,
                PromptVersionCreate(
                    id=approved_prompt_id,
                    agent_id=proposal.agent_id,
                    version=new_version,
                    prompt_text=proposal.new_prompt,
                    is_active=True,
                    created_at=utc_now(),
                    approved_at=utc_now(),
                ),
            )
            proposal.approved_prompt_version_id = approved_prompt_id
        self.db.commit()
        return {
            "rewrite_id": proposal.id,
            "status": proposal.status,
            "approved_prompt_version_id": approved_prompt_id,
            "decided_at": proposal.decided_at,
        }

    def latest_approved_rewrite(self) -> PromptRewriteProposal | None:
        return get_latest_approved_rewrite(self.db)
