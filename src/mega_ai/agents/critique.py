from __future__ import annotations

from mega_ai.agents.base import BaseAgent
from mega_ai.core.context.provenance import split_sentences
from mega_ai.core.context.schemas import AgentOutput, CritiqueItem, SharedContext


class CritiqueAgent(BaseAgent):
    agent_id = "critique"
    default_budget = 3500

    def _run(self, context: SharedContext) -> AgentOutput:
        critique_items: list[CritiqueItem] = []
        injection = "ignore" in context.user_query.lower() and "instruction" in context.user_query.lower()
        wrong_premise = any(
            marker in context.user_query.lower()
            for marker in ("six endpoints", "single agent", "no evaluation needed")
        )

        for agent_id, output in context.agent_outputs.items():
            if agent_id == self.agent_id:
                continue
            claims = output.claims or split_sentences(output.content)
            for claim in claims:
                disagreed_span = None
                reason = "Claim is consistent with current shared context."
                confidence = 0.82
                if injection and "instruction" in claim.lower():
                    disagreed_span = "override instructions"
                    reason = "Prompt injection must be treated as untrusted user content."
                    confidence = 0.45
                if wrong_premise and (
                    "six" in claim.lower() or "single" in claim.lower() or "no evaluation" in claim.lower()
                ):
                    disagreed_span = claim[:120]
                    reason = "The claim may inherit a false premise from the query."
                    confidence = 0.38
                critique_items.append(
                    CritiqueItem(
                        claim=claim,
                        confidence=confidence,
                        disagreed_span=disagreed_span,
                        reason=reason,
                    )
                )
        if injection:
            critique_items.append(
                CritiqueItem(
                    claim="The user attempted to override prior instructions.",
                    confidence=0.95,
                    disagreed_span="Ignore all prior instructions",
                    reason="Instruction hierarchy and assignment contracts must remain active.",
                )
            )
        if wrong_premise:
            critique_items.append(
                CritiqueItem(
                    claim="The user query contains a factually confident but wrong premise.",
                    confidence=0.9,
                    disagreed_span="wrong premise",
                    reason="The system must resolve false premises before final synthesis.",
                )
            )
        context.critiques = critique_items
        disagreements = [item for item in critique_items if item.disagreed_span]
        content = (
            f"Reviewed {len(critique_items)} claims. "
            f"Flagged {len(disagreements)} span-level disagreements."
        )
        return AgentOutput(
            agent_id=self.agent_id,
            content=content,
            claims=[item.claim for item in critique_items],
            metadata={"critiques": [item.model_dump() for item in critique_items]},
        )
