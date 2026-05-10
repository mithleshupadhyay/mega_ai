from __future__ import annotations

from collections import Counter

from mega_ai.evals.cases import EVAL_CASES


def test_eval_harness_has_required_case_distribution() -> None:
    counts = Counter(case.category for case in EVAL_CASES)

    assert len(EVAL_CASES) == 15
    assert counts == {"straightforward": 5, "ambiguous": 5, "adversarial": 5}
