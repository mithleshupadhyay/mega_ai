from __future__ import annotations

from mega_ai.core.context.schemas import SharedContext
from mega_ai.tools.code_sandbox import CodeSandboxTool
from mega_ai.tools.data_lookup import StructuredDataLookupTool
from mega_ai.tools.self_reflection import SelfReflectionTool
from mega_ai.tools.web_search_stub import WebSearchStubTool


def test_web_search_stub_empty_failure_contract() -> None:
    result = WebSearchStubTool().run({"query": "zzzz-no-results"})

    assert result.status == "empty"
    assert result.failure_mode == "empty_result"
    assert result.output == {"results": []}


def test_web_search_stub_rejects_secret_like_input() -> None:
    result = WebSearchStubTool().run({"query": "Authorization: Bearer test"})

    assert result.status == "failed"
    assert result.failure_mode == "unsafe_input"


def test_code_sandbox_rejects_unsafe_input() -> None:
    result = CodeSandboxTool().run({"code": "import os\nprint(os.getcwd())"})

    assert result.status == "failed"
    assert result.failure_mode == "unsafe_input"
    assert result.output["exit_code"] == 126


def test_code_sandbox_empty_result_contract() -> None:
    result = CodeSandboxTool().run({"code": "pass"})

    assert result.status == "empty"
    assert result.failure_mode == "empty_result"


def test_data_lookup_rejects_unsafe_sql_intent(db_session) -> None:
    result = StructuredDataLookupTool(db_session).run({"question": "drop table jobs"})

    assert result.status == "failed"
    assert result.failure_mode == "unsafe_input"


def test_self_reflection_empty_result_contract() -> None:
    context = SharedContext(job_id="job-test", user_query="hello", normalized_query="hello")
    result = SelfReflectionTool(context).run({"focus": "contradictions"})

    assert result.status == "empty"
    assert result.failure_mode == "empty_result"
