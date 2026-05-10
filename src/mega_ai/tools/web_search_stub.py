from __future__ import annotations

import time

from mega_ai.tools.base import ToolResponse

UNSAFE_QUERY_MARKERS = ("authorization:", "bearer ", "api_key", "password", "secret")


class WebSearchStubTool:
    name = "web_search_stub"

    def run(self, payload: dict[str, object]) -> ToolResponse:
        start = time.perf_counter()
        try:
            query = str(payload.get("query", "")).strip()
            if not query:
                return self._response(start, "failed", {}, "malformed_input")
            lowered = query.lower()
            if any(marker in lowered for marker in UNSAFE_QUERY_MARKERS):
                return self._response(
                    start,
                    "failed",
                    {"results": [], "reason": "Unsafe secret-like query rejected."},
                    "unsafe_input",
                )
            if "timeout" in lowered:
                time.sleep(0.01)
                return self._response(start, "failed", {}, "timeout")
            if "zzzz-no-results" in lowered:
                return self._response(start, "empty", {"results": []}, "empty_result")

            results = [
                {
                    "title": "Mega AI assignment brief",
                    "url": "https://devmesh.live/assessments/mega-ai",
                    "snippet": "Multi-agent orchestration, evaluation, tool calling, and streaming traces.",
                    "relevance_score": 0.92,
                },
                {
                    "title": "Production LLM reliability notes",
                    "url": "https://example.com/llm-reliability",
                    "snippet": (
                        "Retries, context budgets, fallback logic, and structured evaluation improve reliability."
                    ),
                    "relevance_score": 0.74,
                },
            ]
            return self._response(start, "ok", {"results": results})
        except Exception as exc:
            return self._response(
                start,
                "failed",
                {"results": [], "error": str(exc)[:200]},
                "execution_error",
            )

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
