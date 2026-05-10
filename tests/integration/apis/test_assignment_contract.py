from __future__ import annotations

from fastapi.testclient import TestClient

from mega_ai.main import app


def test_app_exposes_exactly_five_public_assignment_routes() -> None:
    paths = sorted(route.path for route in app.routes if route.path.startswith("/v1/"))

    assert paths == sorted(
        [
            "/v1/query/stream",
            "/v1/jobs/{job_id}/trace",
            "/v1/evals/latest",
            "/v1/prompts/rewrites/{rewrite_id}/decision",
            "/v1/evals/targeted-rerun",
        ]
    )


def test_streaming_query_persists_trace() -> None:
    with TestClient(app) as client:
        with client.stream(
            "POST",
            "/v1/query/stream",
            json={"query": "How many public API endpoints are required?"},
        ) as response:
            assert response.status_code == 200
            body = "".join(response.iter_text())

        assert "event: final_answer" in body
        job_id = body.split('"job_id": "')[1].split('"')[0]
        trace = client.get(f"/v1/jobs/{job_id}/trace")

    assert trace.status_code == 200
    payload = trace.json()
    assert payload["job"]["status"] == "completed"
    assert any(event["event_type"] == "orchestrator_decision" for event in payload["ordered_events"])
    assert payload["tool_calls"]
    assert "failure_mode" in payload["tool_calls"][0]


def test_eval_latest_and_prompt_approval_flow() -> None:
    with TestClient(app) as client:
        latest = client.get("/v1/evals/latest")
        assert latest.status_code == 200
        data = latest.json()
        assert data["summary"]["case_count"] == 15
        assert data["pending_prompt_rewrites"]
        rewrite_id = data["pending_prompt_rewrites"][0]["rewrite_id"]

        decision = client.post(
            f"/v1/prompts/rewrites/{rewrite_id}/decision",
            json={"decision": "approve", "reviewer_note": "Looks safer."},
        )
        assert decision.status_code == 200
        assert decision.json()["status"] == "approved"

        targeted = client.post("/v1/evals/targeted-rerun", json={})
        assert targeted.status_code == 200
        assert "delta" in targeted.json()
