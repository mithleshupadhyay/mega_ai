from __future__ import annotations

import time

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from mega_ai.tools.base import ToolResponse

UNSAFE_SQL_MARKERS = (
    ";",
    "--",
    "/*",
    "*/",
    " insert ",
    " update ",
    " delete ",
    " drop ",
    " alter ",
    " create ",
    " truncate ",
)


class StructuredDataLookupTool:
    name = "data_lookup"

    def __init__(self, db: Session) -> None:
        self.db = db

    def run(self, payload: dict[str, object]) -> ToolResponse:
        start = time.perf_counter()
        question = str(payload.get("question", "")).strip().lower()
        if not question:
            return self._response(start, "failed", {}, "malformed_input")
        if any(marker in f" {question} " for marker in UNSAFE_SQL_MARKERS):
            return self._response(
                start,
                "failed",
                {"generated_sql": None, "rows": [], "reason": "Unsafe SQL intent rejected."},
                "unsafe_input",
            )
        parsed = self._to_safe_sql(question)
        if parsed is None:
            return self._response(
                start,
                "failed",
                {"generated_sql": None, "rows": []},
                "malformed_input",
            )
        sql, params = parsed
        try:
            rows = [dict(row._mapping) for row in self.db.execute(text(sql), params).all()]
        except SQLAlchemyError as exc:
            return self._response(
                start,
                "failed",
                {"generated_sql": sql, "rows": [], "error": str(exc)[:200]},
                "execution_error",
            )
        if not rows:
            return self._response(start, "empty", {"generated_sql": sql, "rows": []}, "empty_result")
        return self._response(
            start,
            "ok",
            {"generated_sql": sql, "rows": rows, "parse_status": "allowlisted_pattern"},
        )

    def _to_safe_sql(self, question: str) -> tuple[str, dict[str, str]] | None:
        if "endpoint" in question:
            return (
                "select record_key, category, value, metadata_json from structured_records "
                "where record_key = :record_key",
                {"record_key": "required_endpoint_count"},
            )
        if "eval" in question or "test case" in question:
            return (
                "select record_key, category, value, metadata_json from structured_records "
                "where record_key = :record_key",
                {"record_key": "eval_case_count"},
            )
        if "tool" in question:
            return (
                "select record_key, category, value, metadata_json from structured_records "
                "where record_key = :record_key",
                {"record_key": "required_tools"},
            )
        if "agent" in question:
            return (
                "select record_key, category, value, metadata_json from structured_records "
                "where record_key = :record_key",
                {"record_key": "agent_count"},
            )
        return None

    def _response(
        self,
        start: float,
        status: str,
        output: dict[str, object],
        failure_mode: str | None = None,
    ) -> ToolResponse:
        return ToolResponse(
            tool_name=self.name,
            status=status,
            output=output,
            failure_mode=failure_mode,
            latency_ms=int((time.perf_counter() - start) * 1000),
        )
