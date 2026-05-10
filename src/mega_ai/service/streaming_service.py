from __future__ import annotations

import json


def sse(event: str, data: dict[str, object]) -> str:
    return f"event: {event}\ndata: {json.dumps(data, default=str)}\n\n"


def token_events(job_id: str, agent_id: str, text: str) -> list[tuple[str, dict[str, object]]]:
    return [
        ("agent_token", {"job_id": job_id, "agent_id": agent_id, "token": token})
        for token in text.split()
    ]
