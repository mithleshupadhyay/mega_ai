from __future__ import annotations

DEFAULT_PROMPTS = {
    "decomposition": (
        "Break the query into typed subtasks, list dependencies, and keep the dependency graph "
        "explicit. Prefer the smallest useful set of tasks."
    ),
    "retrieval": (
        "Use multi-hop retrieval. Cite at least two retrieved chunks and map each answer claim "
        "to contributing chunks."
    ),
    "critique": (
        "Review each claim separately. Score confidence per claim and flag exact disagreed spans "
        "with reasons."
    ),
    "synthesis": (
        "Merge agent outputs, resolve contradictions, and produce a final answer with provenance "
        "for every sentence."
    ),
    "compression": (
        "Compress old conversational context while preserving structured tool outputs, scores, "
        "citations, and provenance exactly."
    ),
    "meta_prompt": (
        "Inspect eval failures, identify the worst prompt by scoring dimension, and propose a "
        "human-reviewable prompt rewrite with a structured diff."
    ),
}


def prompt_id(agent_id: str, version: int = 1) -> str:
    return f"{agent_id}-v{version}"
