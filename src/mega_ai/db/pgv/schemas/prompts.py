from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class PromptVersionCreate(BaseModel):
    id: str
    agent_id: str
    version: int
    prompt_text: str
    is_active: bool = True
    created_at: datetime
    approved_at: datetime | None = None


class PromptVersionOut(PromptVersionCreate):
    model_config = ConfigDict(from_attributes=True)


class PromptRewriteProposalCreate(BaseModel):
    id: str
    eval_run_id: str
    agent_id: str
    target_dimension: str
    old_prompt: str
    new_prompt: str
    structured_diff: dict[str, Any] = Field(default_factory=dict)
    justification: str
    status: str = "pending"
    created_at: datetime


class PromptRewriteProposalOut(PromptRewriteProposalCreate):
    reviewer_note: str | None = None
    decided_at: datetime | None = None
    approved_prompt_version_id: str | None = None

    model_config = ConfigDict(from_attributes=True)


class PromptRewriteDecision(BaseModel):
    decision: Literal["approve", "reject"]
    reviewer_note: str = ""


class PerformanceDeltaCreate(BaseModel):
    rewrite_id: str
    before_eval_run_id: str
    after_eval_run_id: str
    delta_payload: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class PerformanceDeltaOut(PerformanceDeltaCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)
