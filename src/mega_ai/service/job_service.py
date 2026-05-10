from __future__ import annotations

import uuid
from collections.abc import Iterator

from sqlalchemy.orm import Session

from mega_ai.agents.orchestrator import OrchestratorAgent
from mega_ai.core.context.budget_manager import ContextBudgetManager
from mega_ai.core.context.schemas import SharedContext
from mega_ai.core.logging.redaction import stable_hash
from mega_ai.core.logging.structured import emit_trace, utc_now
from mega_ai.db.pgv.crud.jobs import create_job, get_job, mark_job_completed, mark_job_failed
from mega_ai.db.pgv.crud.seeds import seed_static_data
from mega_ai.db.pgv.schemas.jobs import JobCreate
from mega_ai.service.streaming_service import sse


class JobService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.budget_manager = ContextBudgetManager()

    def run_query_stream(self, query: str) -> Iterator[str]:
        seed_static_data(self.db)
        job_id = f"job-{uuid.uuid4().hex[:12]}"
        now = utc_now()
        create_job(
            self.db,
            JobCreate(
                id=job_id,
                status="running",
                query=query,
                created_at=now,
                updated_at=now,
            ),
        )

        context = SharedContext(job_id=job_id, user_query=query, normalized_query=query.strip().lower())
        emit_trace(self.db, job_id=job_id, event_type="job_started", payload={"query_hash": stable_hash(query)})
        yield sse("job_started", {"job_id": job_id})

        try:
            for event_name, payload in self._run_pipeline(context):
                yield sse(event_name, payload)
            job = get_job(self.db, job_id)
            if job is not None:
                mark_job_completed(
                    self.db,
                    job,
                    final_answer=context.final_answer,
                    provenance_map={"sentences": [item.model_dump() for item in context.provenance_map]},
                    updated_at=utc_now(),
                )
            emit_trace(
                self.db,
                job_id=job_id,
                event_type="job_finished",
                output_text=context.final_answer or "",
                payload={"status": "completed"},
            )
            yield sse(
                "job_finished",
                {
                    "job_id": job_id,
                    "status": "completed",
                    "provenance_sentence_count": len(context.provenance_map),
                },
            )
        except Exception as exc:
            job = get_job(self.db, job_id)
            if job is not None:
                mark_job_failed(self.db, job, error_code="PIPELINE_FAILED", updated_at=utc_now())
            emit_trace(
                self.db,
                job_id=job_id,
                event_type="job_failed",
                payload={"error_code": "PIPELINE_FAILED", "message": str(exc)[:200]},
            )
            yield sse(
                "job_failed",
                {"job_id": job_id, "error_code": "PIPELINE_FAILED", "message": "Pipeline failed."},
            )

    def run_pipeline_for_eval(self, query: str) -> SharedContext:
        seed_static_data(self.db)
        job_id = f"eval-job-{uuid.uuid4().hex[:12]}"
        now = utc_now()
        create_job(
            self.db,
            JobCreate(
                id=job_id,
                status="running",
                query=query,
                created_at=now,
                updated_at=now,
            ),
        )
        context = SharedContext(job_id=job_id, user_query=query, normalized_query=query.strip().lower())
        emit_trace(self.db, job_id=job_id, event_type="job_started", payload={"eval_mode": True})
        for _event_name, _payload in self._run_pipeline(context):
            pass
        job = get_job(self.db, job_id)
        if job:
            mark_job_completed(
                self.db,
                job,
                final_answer=context.final_answer,
                provenance_map={"sentences": [item.model_dump() for item in context.provenance_map]},
                updated_at=utc_now(),
            )
        emit_trace(self.db, job_id=job_id, event_type="job_finished", payload={"eval_mode": True})
        return context

    def _run_pipeline(self, context: SharedContext) -> Iterator[tuple[str, dict[str, object]]]:
        orchestrator = OrchestratorAgent(self.db, self.budget_manager)
        yield from orchestrator.run(context)
