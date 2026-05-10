from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class JobBase(BaseModel):
    query: str
    status: str = "running"


class JobCreate(JobBase):
    id: str
    created_at: datetime
    updated_at: datetime


class JobUpdate(BaseModel):
    status: str | None = None
    final_answer: str | None = None
    provenance_map: dict[str, Any] | None = None
    error_code: str | None = None
    updated_at: datetime


class JobOut(JobBase):
    id: str
    final_answer: str | None = None
    provenance_map: dict[str, Any] = Field(default_factory=dict)
    error_code: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TraceEventCreate(BaseModel):
    job_id: str
    event_order: int
    timestamp: datetime
    event_type: str
    agent_id: str | None = None
    input_hash: str = ""
    output_hash: str = ""
    latency_ms: int | None = None
    token_count: int | None = None
    policy_violations: list[str] = Field(default_factory=list)
    payload: dict[str, Any] = Field(default_factory=dict)


class TraceEventOut(TraceEventCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class AgentExecutionCreate(BaseModel):
    job_id: str
    agent_id: str
    prompt_version_id: str
    prompt_text: str
    input_payload: dict[str, Any] = Field(default_factory=dict)
    output_payload: dict[str, Any] = Field(default_factory=dict)
    started_at: datetime
    finished_at: datetime
    latency_ms: int
    token_count: int


class AgentExecutionOut(AgentExecutionCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)
