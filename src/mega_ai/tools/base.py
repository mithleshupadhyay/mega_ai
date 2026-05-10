from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass
class ToolResponse:
    tool_name: str
    status: str
    output: dict[str, object]
    latency_ms: int
    failure_mode: str | None = None
    accepted: bool = False
    rejection_reason: str | None = None
    metadata: dict[str, object] = field(default_factory=dict)


class Tool(Protocol):
    name: str

    def run(self, payload: dict[str, object]) -> ToolResponse:
        raise NotImplementedError
