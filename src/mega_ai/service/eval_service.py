from __future__ import annotations

import uuid
from typing import cast

from sqlalchemy.orm import Session

from mega_ai.core.logging.structured import utc_now
from mega_ai.db.pgv.crud.evals import (
    create_eval_case_result,
    create_eval_run,
    get_eval_run,
    get_latest_eval_run,
    list_failed_case_results,
    update_eval_run,
)
from mega_ai.db.pgv.crud.prompts import (
    active_prompt_snapshot,
    create_performance_delta,
    list_rewrite_proposals_for_eval,
)
from mega_ai.db.pgv.crud.tools import list_tool_calls_for_job
from mega_ai.db.pgv.models import EvalRun
from mega_ai.db.pgv.schemas.evals import EvalCaseResultCreate, EvalRunCreate, EvalRunUpdate
from mega_ai.db.pgv.schemas.prompts import PerformanceDeltaCreate
from mega_ai.evals.cases import EVAL_CASES, EvalCase
from mega_ai.evals.diff import performance_delta
from mega_ai.evals.scorers import EvalResult, score_case, summarize_results
from mega_ai.service.job_service import JobService
from mega_ai.service.prompt_rewrite_service import PromptRewriteService

EVAL_PIPELINE_VERSION = "2026-05-10-endpoint-citation-budget-v2"


class EvalService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def latest_or_run(self) -> dict[str, object]:
        latest = get_latest_eval_run(self.db)
        if latest is None or not self._is_current_eval(latest):
            latest = self.run_full_eval()
        return self._serialize_eval(latest)

    def run_full_eval(self) -> EvalRun:
        return self._run_eval(EVAL_CASES, run_type="full")

    def run_targeted_failed_cases(self, eval_run_id: str | None = None) -> dict[str, object]:
        before = self._find_eval(eval_run_id)
        if before is None:
            before = self.run_full_eval()
        failed_rows = list_failed_case_results(self.db, before.id)
        failed_ids = {row.test_case_id for row in failed_rows}
        cases = [case for case in EVAL_CASES if case.id in failed_ids] or EVAL_CASES
        after = self._run_eval(cases, run_type="targeted")
        delta = performance_delta(cast(dict[str, object], before.summary), cast(dict[str, object], after.summary))
        rewrite = PromptRewriteService(self.db).latest_approved_rewrite()
        if rewrite:
            create_performance_delta(
                self.db,
                PerformanceDeltaCreate(
                    rewrite_id=rewrite.id,
                    before_eval_run_id=before.id,
                    after_eval_run_id=after.id,
                    delta_payload=delta,
                    created_at=utc_now(),
                )
            )
        return {"before_eval_run_id": before.id, "after_eval_run": self._serialize_eval(after), "delta": delta}

    def _run_eval(self, cases: list[EvalCase], *, run_type: str) -> EvalRun:
        eval_run_id = f"eval-{uuid.uuid4().hex[:12]}"
        eval_run = create_eval_run(
            self.db,
            EvalRunCreate(
                id=eval_run_id,
                status="running",
                run_type=run_type,
                started_at=utc_now(),
                summary={},
                prompt_version_ids=active_prompt_snapshot(self.db),
            ),
        )

        results: list[EvalResult] = []
        job_service = JobService(self.db)
        for case in cases:
            context = job_service.run_pipeline_for_eval(case.query)
            scored = score_case(case, context)
            tool_calls = list_tool_calls_for_job(self.db, context.job_id)
            result_payload: EvalResult = {
                "test_case_id": case.id,
                "category": case.category,
                "job_id": context.job_id,
                "scores": scored["scores"],
                "total_score": scored["total_score"],
                "passed": scored["passed"],
                "final_answer": context.final_answer,
            }
            results.append(result_payload)
            create_eval_case_result(
                self.db,
                EvalCaseResultCreate(
                    eval_run_id=eval_run_id,
                    test_case_id=case.id,
                    category=case.category,
                    job_id=context.job_id,
                    prompt_snapshots=active_prompt_snapshot(self.db),
                    tool_calls=[
                        {
                            "tool_name": row.tool_name,
                            "status": row.status,
                            "accepted": row.accepted,
                            "retry_number": row.retry_number,
                        }
                        for row in tool_calls
                    ],
                    outputs={
                        "final_answer": context.final_answer,
                        "agent_outputs": {
                            key: value.model_dump() for key, value in context.agent_outputs.items()
                        },
                    },
                    scores=scored["scores"],
                    total_score=scored["total_score"],
                    passed=scored["passed"],
                    diffable_snapshot={
                        "case_id": case.id,
                        "answer": context.final_answer,
                        "scores": scored["scores"],
                        "tool_calls": len(tool_calls),
                    },
                    created_at=utc_now(),
                )
            )
        summary = summarize_results(results)
        summary["pipeline_version"] = EVAL_PIPELINE_VERSION
        update_eval_run(
            self.db,
            eval_run,
            EvalRunUpdate(status="completed", finished_at=utc_now(), summary=summary),
        )
        self._maybe_propose_rewrite(eval_run, summary)
        self.db.refresh(eval_run)
        return eval_run

    def _is_current_eval(self, eval_run: EvalRun) -> bool:
        summary = eval_run.summary if isinstance(eval_run.summary, dict) else {}
        return summary.get("pipeline_version") == EVAL_PIPELINE_VERSION

    def _maybe_propose_rewrite(self, eval_run: EvalRun, summary: dict[str, object]) -> None:
        dimension_totals: dict[str, list[float]] = {}
        categories = summary.get("categories", {})
        if not isinstance(categories, dict):
            return
        for category_data in categories.values():
            if not isinstance(category_data, dict):
                continue
            dimensions = category_data.get("dimensions", {})
            if not isinstance(dimensions, dict):
                continue
            for dimension, score in dimensions.items():
                if isinstance(dimension, str) and isinstance(score, int | float):
                    dimension_totals.setdefault(dimension, []).append(float(score))
        if not dimension_totals:
            return
        averages = {
            dimension: sum(values) / len(values) for dimension, values in dimension_totals.items()
        }
        worst_dimension = min(averages, key=lambda name: averages[name])
        target_agent = "retrieval" if "citation" in worst_dimension else "critique"
        existing = get_eval_run(self.db, eval_run.id)
        if existing:
            PromptRewriteService(self.db).propose_from_eval(
                eval_run_id=eval_run.id,
                summary=summary,
                worst_dimension=worst_dimension,
                target_agent=target_agent,
            )

    def _find_eval(self, eval_run_id: str | None) -> EvalRun | None:
        if eval_run_id:
            return get_eval_run(self.db, eval_run_id)
        return get_latest_eval_run(self.db)

    def _serialize_eval(self, eval_run: EvalRun) -> dict[str, object]:
        proposals = list_rewrite_proposals_for_eval(self.db, eval_run.id)
        return {
            "eval_run_id": eval_run.id,
            "status": eval_run.status,
            "run_type": eval_run.run_type,
            "started_at": eval_run.started_at,
            "finished_at": eval_run.finished_at,
            "summary": eval_run.summary,
            "prompt_version_ids": eval_run.prompt_version_ids,
            "pending_prompt_rewrites": [
                {
                    "rewrite_id": proposal.id,
                    "agent_id": proposal.agent_id,
                    "target_dimension": proposal.target_dimension,
                    "status": proposal.status,
                    "structured_diff": proposal.structured_diff,
                    "justification": proposal.justification,
                }
                for proposal in proposals
                if proposal.status == "pending"
            ],
        }
