from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str = Field(min_length=1, max_length=4000)
    metadata: dict[str, str] = Field(default_factory=dict)


class PromptRewriteDecisionRequest(BaseModel):
    decision: Literal["approve", "reject"]
    reviewer_note: str = Field(default="", max_length=1000)


class TargetedRerunRequest(BaseModel):
    eval_run_id: str | None = None


class ErrorResponse(BaseModel):
    error_code: str
    message: str
    job_id: str | None = None
