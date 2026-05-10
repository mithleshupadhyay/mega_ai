from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypedDict

from mega_ai.core.context.schemas import SharedContext
from mega_ai.evals.cases import EvalCase


class ScoreDetail(TypedDict):
    score: float
    justification: str


class CaseScore(TypedDict):
    scores: dict[str, ScoreDetail]
    total_score: float
    passed: bool


class EvalResult(TypedDict):
    test_case_id: str
    category: str
    job_id: str
    scores: dict[str, ScoreDetail]
    total_score: float
    passed: bool
    final_answer: str | None


@dataclass
class CategoryAccumulator:
    case_count: int = 0
    passed_count: int = 0
    total_score_sum: float = 0.0
    dimension_sums: dict[str, float] = field(default_factory=dict)


DIMENSIONS = [
    "answer_correctness",
    "citation_accuracy",
    "contradiction_resolution_quality",
    "tool_selection_efficiency",
    "context_budget_compliance",
    "critique_agreement_rate",
]


def score_case(case: EvalCase, context: SharedContext) -> CaseScore:
    answer = (context.final_answer or "").lower()
    tool_count = len(context.tool_results)
    citations = [str(chunk["chunk_id"]) for chunk in context.retrieved_chunks]
    violations = context.policy_violations
    disagreements = [item for item in context.critiques if item.disagreed_span]

    keyword_hits = sum(1 for keyword in case.expected_keywords if keyword.lower() in answer)
    correctness = keyword_hits / max(1, len(case.expected_keywords))

    citation_accuracy = 1.0 if len(set(citations)) >= 2 else 0.4 if citations else 0.0

    contradiction_resolution = 1.0
    if case.requires_contradiction_resolution:
        contradiction_resolution = 1.0 if "resolved" in answer and disagreements else 0.35
    elif disagreements and "resolved" not in answer:
        contradiction_resolution = 0.5

    tool_selection_efficiency = max(0.0, 1.0 - max(0, tool_count - case.expected_tool_max) * 0.25)
    context_budget_compliance = 0.0 if any("context_budget_overflow" in v for v in violations) else 1.0
    critique_agreement = 0.5
    if context.critiques:
        critique_agreement = 1.0 if not disagreements or "resolved" in answer else 0.0

    scores: dict[str, ScoreDetail] = {
        "answer_correctness": {
            "score": round(correctness, 3),
            "justification": f"Matched {keyword_hits}/{len(case.expected_keywords)} expected keywords.",
        },
        "citation_accuracy": {
            "score": citation_accuracy,
            "justification": f"Used {len(set(citations))} distinct retrieved chunk citations.",
        },
        "contradiction_resolution_quality": {
            "score": contradiction_resolution,
            "justification": (
                "Contradictions were resolved in final synthesis."
                if contradiction_resolution == 1.0
                else "Expected contradiction handling was incomplete."
            ),
        },
        "tool_selection_efficiency": {
            "score": round(tool_selection_efficiency, 3),
            "justification": f"Used {tool_count} tools with expected maximum {case.expected_tool_max}.",
        },
        "context_budget_compliance": {
            "score": context_budget_compliance,
            "justification": (
                "No context budget overflow policy violations."
                if context_budget_compliance == 1.0
                else "Context budget overflow policy violation detected."
            ),
        },
        "critique_agreement_rate": {
            "score": critique_agreement,
            "justification": (
                "Critique disagreements are absent or resolved in final output."
                if critique_agreement == 1.0
                else "Critique disagreement was not clearly resolved."
            ),
        },
    }
    total = (
        correctness
        + citation_accuracy
        + contradiction_resolution
        + tool_selection_efficiency
        + context_budget_compliance
        + critique_agreement
    ) / len(scores)
    return {"scores": scores, "total_score": round(total, 3), "passed": total >= 0.72}


def summarize_results(results: list[EvalResult]) -> dict[str, object]:
    categories: dict[str, CategoryAccumulator] = {}
    for result in results:
        bucket = categories.setdefault(
            result["category"],
            CategoryAccumulator(dimension_sums={dimension: 0.0 for dimension in DIMENSIONS}),
        )
        bucket.case_count += 1
        bucket.passed_count += 1 if result["passed"] else 0
        bucket.total_score_sum += result["total_score"]
        for dimension in DIMENSIONS:
            bucket.dimension_sums[dimension] += result["scores"][dimension]["score"]

    category_summary = {
        category: {
            "case_count": bucket.case_count,
            "passed_count": bucket.passed_count,
            "average_total_score": round(bucket.total_score_sum / bucket.case_count, 3),
            "dimensions": {
                dimension: round(score_sum / bucket.case_count, 3)
                for dimension, score_sum in bucket.dimension_sums.items()
            },
        }
        for category, bucket in categories.items()
    }
    overall = (
        round(sum(result["total_score"] for result in results) / len(results), 3) if results else 0.0
    )
    return {
        "case_count": len(results),
        "passed_count": sum(1 for result in results if result["passed"]),
        "average_total_score": overall,
        "categories": category_summary,
    }
