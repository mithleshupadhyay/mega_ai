from __future__ import annotations


def performance_delta(before: dict[str, object], after: dict[str, object]) -> dict[str, object]:
    before_score_value = before.get("average_total_score", 0)
    after_score_value = after.get("average_total_score", 0)
    before_score = float(before_score_value) if isinstance(before_score_value, int | float) else 0.0
    after_score = float(after_score_value) if isinstance(after_score_value, int | float) else 0.0
    return {
        "before_average_total_score": before_score,
        "after_average_total_score": after_score,
        "delta": round(
            after_score - before_score,
            3,
        ),
        "before_passed_count": before.get("passed_count", 0),
        "after_passed_count": after.get("passed_count", 0),
    }
