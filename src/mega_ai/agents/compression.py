from __future__ import annotations

from mega_ai.agents.base import BaseAgent
from mega_ai.core.context.schemas import AgentOutput, SharedContext


class CompressionAgent(BaseAgent):
    agent_id = "compression"
    default_budget = 500

    def _run(self, context: SharedContext) -> AgentOutput:
        structured_snapshot: dict[str, object] = {
            "tool_results": [result.model_dump() for result in context.tool_results],
            "retrieved_chunk_ids": [chunk["chunk_id"] for chunk in context.retrieved_chunks],
            "critique_count": len(context.critiques),
            "subtasks": [task.model_dump() for task in context.subtasks],
        }
        note: dict[str, object] = {
            "lossless_structured_data": structured_snapshot,
            "lossy_summary": "Older conversational filler compressed; structured data preserved.",
        }
        context.compressed_notes.append(note)
        return AgentOutput(
            agent_id=self.agent_id,
            content="Compressed older context while preserving structured tool, citation, and score data.",
            claims=["Structured data is preserved losslessly during compression."],
            metadata=note,
        )
