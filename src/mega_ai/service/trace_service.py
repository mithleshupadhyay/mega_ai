from __future__ import annotations

from sqlalchemy.orm import Session

from mega_ai.db.pgv.crud.jobs import get_job
from mega_ai.db.pgv.crud.tools import list_tool_calls_for_job
from mega_ai.db.pgv.crud.traces import list_trace_events
from mega_ai.db.pgv.models import AgentExecution


class TraceService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_trace(self, job_id: str) -> dict[str, object] | None:
        job = get_job(self.db, job_id)
        if job is None:
            return None
        traces = list_trace_events(self.db, job_id)
        agent_executions = (
            self.db.query(AgentExecution)
            .filter(AgentExecution.job_id == job_id)
            .order_by(AgentExecution.started_at.asc())
            .all()
        )
        tool_calls = list_tool_calls_for_job(self.db, job_id)
        return {
            "job": {
                "job_id": job.id,
                "status": job.status,
                "created_at": job.created_at,
                "updated_at": job.updated_at,
                "final_answer": job.final_answer,
                "provenance_map": job.provenance_map,
                "error_code": job.error_code,
            },
            "ordered_events": [
                {
                    "event_order": event.event_order,
                    "timestamp": event.timestamp,
                    "agent_id": event.agent_id,
                    "event_type": event.event_type,
                    "input_hash": event.input_hash,
                    "output_hash": event.output_hash,
                    "latency_ms": event.latency_ms,
                    "token_count": event.token_count,
                    "policy_violations": event.policy_violations,
                    "payload": event.payload,
                }
                for event in traces
            ],
            "agent_executions": [
                {
                    "agent_id": row.agent_id,
                    "prompt_version_id": row.prompt_version_id,
                    "prompt_text": row.prompt_text,
                    "input_payload": row.input_payload,
                    "output_payload": row.output_payload,
                    "latency_ms": row.latency_ms,
                    "token_count": row.token_count,
                }
                for row in agent_executions
            ],
            "tool_calls": [
                {
                    "tool_call_id": row.tool_call_id,
                    "tool_name": row.tool_name,
                    "agent_id": row.agent_id,
                    "retry_number": row.retry_number,
                    "status": row.status,
                    "failure_mode": row.failure_mode,
                    "input_hash": row.input_hash,
                    "input_preview": row.input_preview,
                    "output_hash": row.output_hash,
                    "output_payload": row.output_payload,
                    "accepted": row.accepted,
                    "rejection_reason": row.rejection_reason,
                    "latency_ms": row.latency_ms,
                }
                for row in tool_calls
            ],
        }
