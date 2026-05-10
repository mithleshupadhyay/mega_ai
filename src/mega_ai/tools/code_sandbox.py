from __future__ import annotations

import subprocess
import sys
import time

from mega_ai.core.config import get_settings
from mega_ai.tools.base import ToolResponse

UNSAFE_MARKERS = (
    "import os",
    "import sys",
    "subprocess",
    "socket",
    "open(",
    "exec(",
    "eval(",
    "__import__",
    "pathlib",
)


class CodeSandboxTool:
    name = "code_sandbox"

    def run(self, payload: dict[str, object]) -> ToolResponse:
        start = time.perf_counter()
        code = str(payload.get("code", "")).strip()
        if not code:
            return self._response(start, "failed", {}, "malformed_input")
        lowered = code.lower()
        if any(marker in lowered for marker in UNSAFE_MARKERS):
            return self._response(
                start,
                "failed",
                {"stderr": "Unsafe code rejected by sandbox policy.", "exit_code": 126},
                "unsafe_input",
            )
        try:
            completed = subprocess.run(
                [sys.executable, "-I", "-c", code],
                capture_output=True,
                text=True,
                timeout=get_settings().code_sandbox_timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            return self._response(
                start,
                "failed",
                {
                    "stdout": exc.stdout or "",
                    "stderr": "Execution timed out.",
                    "exit_code": 124,
                    "timeout": True,
                },
                "timeout",
            )
        if completed.returncode == 0 and not completed.stdout.strip() and not completed.stderr.strip():
            return self._response(
                start,
                "empty",
                {
                    "stdout": "",
                    "stderr": "",
                    "exit_code": completed.returncode,
                    "timeout": False,
                },
                "empty_result",
            )
        status = "ok" if completed.returncode == 0 else "failed"
        return self._response(
            start,
            status,
            {
                "stdout": completed.stdout,
                "stderr": completed.stderr,
                "exit_code": completed.returncode,
                "timeout": False,
            },
            None if completed.returncode == 0 else "execution_error",
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
