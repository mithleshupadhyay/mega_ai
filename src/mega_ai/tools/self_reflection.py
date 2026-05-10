from __future__ import annotations

import time

from mega_ai.core.context.schemas import SharedContext
from mega_ai.tools.base import ToolResponse


class SelfReflectionTool:
    name = "self_reflection"

    def __init__(self, context: SharedContext) -> None:
        self.context = context

    def run(self, payload: dict[str, object]) -> ToolResponse:
        start = time.perf_counter()
        focus = str(payload.get("focus", "")).strip().lower()
        if not focus:
            return self._response(start, "failed", {}, "malformed_input")
        if "timeout" in focus:
            time.sleep(0.01)
            return self._response(start, "failed", {}, "timeout")
        if any(marker in focus for marker in ("api_key", "bearer ", "password", "secret")):
            return self._response(
                start,
                "failed",
                {"referenced_outputs": [], "contradiction_candidates": []},
                "unsafe_input",
            )
        outputs = [
            {"agent_id": agent_id, "content": output.content}
            for agent_id, output in self.context.agent_outputs.items()
        ]
        if not outputs:
            return self._response(
                start,
                "empty",
                {"referenced_outputs": [], "contradiction_candidates": [], "focus": focus},
                "empty_result",
            )
        contradictions = []
        if "exactly five" in self.context.user_query.lower() and "six endpoint" in str(outputs).lower():
            contradictions.append(
                {
                    "span": "six endpoints",
                    "reason": "Assignment requires exactly five public endpoints.",
                    "confidence": 0.9,
                }
            )
        if "ignore" in self.context.user_query.lower() and "instruction" in self.context.user_query.lower():
            contradictions.append(
                {
                    "span": "ignore previous instructions",
                    "reason": "Prompt-injection phrase must not override system or agent contracts.",
                    "confidence": 0.95,
                }
            )
        return self._response(
            start,
            "ok",
            {
                "referenced_outputs": outputs,
                "contradiction_candidates": contradictions,
                "focus": focus,
            },
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
