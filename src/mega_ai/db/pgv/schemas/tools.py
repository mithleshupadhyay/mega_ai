from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ToolCallCreate(BaseModel):
    job_id: str
    tool_call_id: str
    tool_name: str
    agent_id: str
    retry_number: int = 0
    status: str
    failure_mode: str | None = None
    input_hash: str
    input_preview: str
    output_hash: str
    output_payload: dict[str, Any] = Field(default_factory=dict)
    accepted: bool = False
    rejection_reason: str | None = None
    latency_ms: int
    created_at: datetime


class ToolCallOut(ToolCallCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)
