from __future__ import annotations

from mega_ai.core.context.budget_manager import ContextBudgetManager
from mega_ai.core.context.schemas import SharedContext


def test_context_budget_overflow_is_policy_violation() -> None:
    context = SharedContext(job_id="job-test", user_query="hello", normalized_query="hello")
    manager = ContextBudgetManager()
    manager.declare_budget(context, "retrieval", 2)

    accepted = manager.add_context(context, "retrieval", "one two three four")

    assert accepted is False
    assert any("context_budget_overflow" in violation for violation in context.policy_violations)
