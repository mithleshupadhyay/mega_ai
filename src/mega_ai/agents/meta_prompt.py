from __future__ import annotations

from mega_ai.agents.base import BaseAgent
from mega_ai.core.context.schemas import AgentOutput, SharedContext


class MetaPromptAgent(BaseAgent):
    agent_id = "meta_prompt"
    default_budget = 700

    def _run(self, context: SharedContext) -> AgentOutput:
        failure_summary = context.metadata.get("failure_summary", {})
        failure_data = failure_summary if isinstance(failure_summary, dict) else {}
        target_agent = str(failure_data.get("agent_id", "retrieval"))
        target_dimension = str(failure_data.get("dimension", "citation_accuracy"))
        content = (
            f"Prompt rewrite recommended for {target_agent} targeting {target_dimension}. "
            "The rewrite should make evidence requirements and rejection criteria more explicit."
        )
        return AgentOutput(
            agent_id=self.agent_id,
            content=content,
            claims=["Prompt rewrites must be stored for human approval before activation."],
            metadata={
                "target_agent": target_agent,
                "target_dimension": target_dimension,
                "rewrite_hint": (
                    "Add explicit acceptance criteria, citation checks, and failure fallback language."
                ),
            },
        )
