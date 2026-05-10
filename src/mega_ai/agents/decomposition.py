from __future__ import annotations

from mega_ai.agents.base import BaseAgent
from mega_ai.core.context.schemas import AgentOutput, SharedContext, SubTask


class DecompositionAgent(BaseAgent):
    agent_id = "decomposition"
    default_budget = 2000

    def _run(self, context: SharedContext) -> AgentOutput:
        query = context.user_query.lower()
        tasks: list[SubTask] = [
            SubTask(
                id="task-1",
                task_type="intent_analysis",
                description="Clarify the user goal and identify ambiguity or adversarial instructions.",
                dependencies=[],
                context_budget=140,
            )
        ]
        if any(term in query for term in ("cite", "source", "assignment", "architecture", "agent")):
            tasks.append(
                SubTask(
                    id="task-2",
                    task_type="multi_hop_retrieval",
                    description="Retrieve at least two relevant chunks and map claims to chunk IDs.",
                    dependencies=["task-1"],
                    context_budget=240,
                )
            )
        if any(term in query for term in ("calculate", "python", "code", "sql", "database", "tool")):
            tasks.append(
                SubTask(
                    id="task-3",
                    task_type="tool_call",
                    description="Use explicit tool interfaces and inspect tool failure contracts.",
                    dependencies=["task-1"],
                    context_budget=220,
                )
            )
        tasks.append(
            SubTask(
                id="task-4",
                task_type="critique_and_synthesis",
                description="Critique claims, resolve contradictions, and produce final provenance.",
                dependencies=[task.id for task in tasks],
                context_budget=290,
            )
        )
        context.subtasks = tasks
        dependency_lines = [
            f"{task.id}:{task.task_type} deps={','.join(task.dependencies) or 'none'}"
            for task in tasks
        ]
        content = "Decomposed query into " + "; ".join(dependency_lines)
        return AgentOutput(
            agent_id=self.agent_id,
            content=content,
            claims=[
                "The query requires explicit task dependency handling.",
                "The critique and synthesis step depends on earlier agent outputs.",
            ],
            metadata={"subtasks": [task.model_dump() for task in tasks]},
        )
