from __future__ import annotations

from mega_ai.agents.orchestrator import OrchestratorAgent
from mega_ai.core.context.budget_manager import ContextBudgetManager
from mega_ai.core.context.schemas import SharedContext


def test_orchestrator_routing_is_query_dependent(db_session) -> None:
    context = SharedContext(
        job_id="job-test",
        user_query="Calculate with python and check database endpoint count.",
        normalized_query="calculate with python and check database endpoint count.",
    )
    decision = OrchestratorAgent(db_session, ContextBudgetManager())._routing_decision(context)

    tool_names = [item[0] for item in decision["tool_plan"]]

    assert "code_sandbox" in tool_names
    assert "data_lookup" in tool_names
    assert decision["selected_agents"] == ["decomposition", "retrieval", "critique", "synthesis"]
    assert "justification" in decision


def test_orchestrator_persists_tool_failure_mode(db_session) -> None:
    context = SharedContext(
        job_id="job-test",
        user_query="Search zzzz-no-results",
        normalized_query="search zzzz-no-results",
    )
    from mega_ai.core.logging.structured import utc_now
    from mega_ai.db.pgv.crud.jobs import create_job
    from mega_ai.db.pgv.models import ToolCall
    from mega_ai.db.pgv.schemas.jobs import JobCreate

    now = utc_now()
    create_job(
        db_session,
        JobCreate(id="job-test", status="running", query=context.user_query, created_at=now, updated_at=now),
    )

    events = list(
        OrchestratorAgent(db_session, ContextBudgetManager())._execute_tool_with_fallback(
            context,
            "web_search_stub",
            {"query": "zzzz-no-results"},
            agent_id="orchestrator",
        )
    )

    rows = db_session.query(ToolCall).filter(ToolCall.job_id == "job-test").all()
    assert any(event_name == "tool_output_rejected" for event_name, _payload in events)
    assert rows[0].failure_mode == "empty_result"
    assert rows[-1].accepted is True
