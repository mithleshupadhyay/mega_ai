from __future__ import annotations

from mega_ai.core.context.schemas import ProvenanceSentence


def split_sentences(text: str) -> list[str]:
    parts = [part.strip() for part in text.replace("\n", " ").split(".")]
    return [f"{part}." for part in parts if part]


def build_provenance(
    final_answer: str,
    *,
    source_agents: list[str],
    source_chunks: list[str],
    source_tool_calls: list[str],
    critique_status: str,
) -> list[ProvenanceSentence]:
    return [
        ProvenanceSentence(
            sentence=sentence,
            source_agents=source_agents,
            source_chunks=source_chunks,
            source_tool_calls=source_tool_calls,
            critique_status=critique_status,
        )
        for sentence in split_sentences(final_answer)
    ]
