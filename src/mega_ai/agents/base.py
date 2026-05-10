from __future__ import annotations

import time
from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from mega_ai.core.context.budget_manager import ContextBudgetManager, estimate_tokens
from mega_ai.core.context.schemas import AgentOutput, SharedContext
from mega_ai.core.logging.structured import utc_now
from mega_ai.db.pgv.crud.jobs import create_agent_execution
from mega_ai.db.pgv.crud.prompts import get_active_prompt
from mega_ai.db.pgv.schemas.jobs import AgentExecutionCreate


class BaseAgent(ABC):
    agent_id: str
    default_budget: int

    def __init__(self, db: Session, budget_manager: ContextBudgetManager) -> None:
        self.db = db
        self.budget_manager = budget_manager

    def execute(self, context: SharedContext) -> AgentOutput:
        prompt = get_active_prompt(self.db, self.agent_id)
        self.budget_manager.declare_budget(context, self.agent_id, self.default_budget)
        self.budget_manager.add_context(
            context,
            self.agent_id,
            {"prompt": prompt.prompt_text, "query": context.user_query},
        )
        started = utc_now()
        start = time.perf_counter()
        output = self._run(context)
        latency_ms = int((time.perf_counter() - start) * 1000)
        finished = utc_now()
        self.budget_manager.add_context(context, self.agent_id, output.model_dump())
        context.add_agent_output(output)

        create_agent_execution(
            self.db,
            AgentExecutionCreate(
                job_id=context.job_id,
                agent_id=self.agent_id,
                prompt_version_id=prompt.id,
                prompt_text=prompt.prompt_text,
                input_payload=self.safe_input_payload(context),
                output_payload=output.model_dump(),
                started_at=started,
                finished_at=finished,
                latency_ms=latency_ms,
                token_count=estimate_tokens(output.content),
            )
        )
        return output

    def safe_input_payload(self, context: SharedContext) -> dict[str, object]:
        return {
            "job_id": context.job_id,
            "query_hash_source": context.normalized_query,
            "available_agent_outputs": sorted(context.agent_outputs.keys()),
            "retrieved_chunk_ids": [chunk["chunk_id"] for chunk in context.retrieved_chunks],
        }

    @abstractmethod
    def _run(self, context: SharedContext) -> AgentOutput:
        raise NotImplementedError
