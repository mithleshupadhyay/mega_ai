from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

AgentId = Literal[
    "orchestrator",
    "decomposition",
    "retrieval",
    "critique",
    "synthesis",
    "compression",
    "meta_prompt",
]


class ContextBudget(BaseModel):
    agent_id: str
    max_tokens: int
    used_tokens: int = 0
    compressed: bool = False

    @property
    def remaining_tokens(self) -> int:
        return max(0, self.max_tokens - self.used_tokens)


class SubTask(BaseModel):
    id: str
    task_type: str
    description: str
    dependencies: list[str] = Field(default_factory=list)
    context_budget: int
    status: str = "pending"


class AgentOutput(BaseModel):
    agent_id: str
    content: str
    claims: list[str] = Field(default_factory=list)
    citations: list[dict[str, object]] = Field(default_factory=list)
    metadata: dict[str, object] = Field(default_factory=dict)


class ToolResult(BaseModel):
    tool_name: str
    status: str
    output: dict[str, object]
    latency_ms: int
    retry_number: int = 0
    accepted: bool = False
    rejection_reason: str | None = None


class CritiqueItem(BaseModel):
    claim: str
    confidence: float
    disagreed_span: str | None = None
    reason: str


class ProvenanceSentence(BaseModel):
    sentence: str
    source_agents: list[str]
    source_chunks: list[str] = Field(default_factory=list)
    source_tool_calls: list[str] = Field(default_factory=list)
    critique_status: str = "supported"


class SharedContext(BaseModel):
    job_id: str
    user_query: str
    normalized_query: str
    budgets: dict[str, ContextBudget] = Field(default_factory=dict)
    subtasks: list[SubTask] = Field(default_factory=list)
    agent_outputs: dict[str, AgentOutput] = Field(default_factory=dict)
    tool_results: list[ToolResult] = Field(default_factory=list)
    retrieved_chunks: list[dict[str, object]] = Field(default_factory=list)
    critiques: list[CritiqueItem] = Field(default_factory=list)
    provenance_map: list[ProvenanceSentence] = Field(default_factory=list)
    routing_decisions: list[dict[str, object]] = Field(default_factory=list)
    policy_violations: list[str] = Field(default_factory=list)
    compressed_notes: list[dict[str, object]] = Field(default_factory=list)
    final_answer: str | None = None
    metadata: dict[str, object] = Field(default_factory=dict)

    def add_agent_output(self, output: AgentOutput) -> None:
        self.agent_outputs[output.agent_id] = output


class StreamEvent(BaseModel):
    event: str
    job_id: str
    data: dict[str, object] = Field(default_factory=dict)
