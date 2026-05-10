from __future__ import annotations

import re
from collections import Counter

from sqlalchemy.orm import Session

from mega_ai.db.pgv.crud.knowledge import list_retrieved_chunks
from mega_ai.db.pgv.models import RetrievedChunk

WORD_PATTERN = re.compile(r"[a-zA-Z0-9_]+")


def normalize_token(token: str) -> str:
    token = token.lower()
    if len(token) > 3 and token.endswith("s"):
        return token[:-1]
    return token


def tokenize(text: str) -> list[str]:
    return [normalize_token(token) for token in WORD_PATTERN.findall(text)]


class LocalRetriever:
    def __init__(self, db: Session) -> None:
        self.db = db

    def retrieve(self, query: str, *, top_k: int = 3) -> list[dict[str, object]]:
        query_terms = Counter(tokenize(query))
        chunks = list_retrieved_chunks(self.db)
        scored: list[tuple[float, RetrievedChunk]] = []
        for chunk in chunks:
            tags = [str(tag) for tag in chunk.tags]
            chunk_terms = Counter(tokenize(f"{chunk.title} {chunk.content} {' '.join(tags)}"))
            overlap = sum(min(query_terms[term], chunk_terms[term]) for term in query_terms)
            normalized_query = set(tokenize(query))
            tag_bonus = sum(1 for tag in tags if normalize_token(tag) in normalized_query) * 0.5
            score = overlap + tag_bonus
            if score > 0:
                scored.append((score, chunk))
        if not scored:
            scored = [(0.1, chunk) for chunk in chunks[:top_k]]
        scored.sort(key=lambda item: (-item[0], item[1].chunk_id))
        return [
            {
                "chunk_id": chunk.chunk_id,
                "title": chunk.title,
                "content": chunk.content,
                "source_url": chunk.source_url,
                "tags": tags,
                "relevance_score": round(score, 3),
            }
            for score, chunk in scored[:top_k]
        ]
