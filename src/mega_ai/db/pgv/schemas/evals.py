from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class EvalRunCreate(BaseModel):
    id: str
    status: str
    run_type: str
    started_at: datetime
    summary: dict[str, Any] = Field(default_factory=dict)
    prompt_version_ids: dict[str, str] = Field(default_factory=dict)


class EvalRunUpdate(BaseModel):
    status: str | None = None
    finished_at: datetime | None = None
    summary: dict[str, Any] | None = None


class EvalRunOut(EvalRunCreate):
    finished_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class EvalCaseResultCreate(BaseModel):
    eval_run_id: str
    test_case_id: str
    category: str
    job_id: str
    prompt_snapshots: dict[str, str] = Field(default_factory=dict)
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    outputs: dict[str, Any] = Field(default_factory=dict)
    scores: dict[str, Any] = Field(default_factory=dict)
    total_score: float
    passed: bool
    diffable_snapshot: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class EvalCaseResultOut(EvalCaseResultCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)
