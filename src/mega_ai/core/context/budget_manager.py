from __future__ import annotations

import re

from mega_ai.core.context.schemas import ContextBudget, SharedContext

TOKEN_PATTERN = re.compile(r"\w+|[^\w\s]")


def estimate_tokens(value: object) -> int:
    text = value if isinstance(value, str) else str(value)
    return max(1, len(TOKEN_PATTERN.findall(text)))


class ContextBudgetManager:
    def declare_budget(self, context: SharedContext, agent_id: str, max_tokens: int) -> ContextBudget:
        budget = ContextBudget(agent_id=agent_id, max_tokens=max_tokens)
        context.budgets[agent_id] = budget
        return budget

    def remaining_budget(self, context: SharedContext, agent_id: str) -> int:
        budget = context.budgets.get(agent_id)
        if budget is None:
            violation = f"{agent_id}:missing_budget_declaration"
            context.policy_violations.append(violation)
            return 0
        return budget.remaining_tokens

    def add_context(self, context: SharedContext, agent_id: str, payload: object) -> bool:
        budget = context.budgets.get(agent_id)
        if budget is None:
            context.policy_violations.append(f"{agent_id}:missing_budget_declaration")
            return False
        token_count = estimate_tokens(payload)
        budget.used_tokens += token_count
        if budget.used_tokens > budget.max_tokens:
            context.policy_violations.append(
                f"{agent_id}:context_budget_overflow:{budget.used_tokens}>{budget.max_tokens}"
            )
            return False
        return True

    def needs_compression(self, context: SharedContext, agent_id: str, payload: object) -> bool:
        budget = context.budgets.get(agent_id)
        if budget is None:
            return True
        return budget.used_tokens + estimate_tokens(payload) > budget.max_tokens
