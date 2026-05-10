# Operations Notes

## Start

```bash
make docker-up-build
```

This starts containers in detached mode. If you run raw `docker compose up --build`,
Docker Compose attaches to service logs in the current terminal by default.

## Logs

```bash
make docker-logs
make docker-logs SERVICE=api
make docker-logs SERVICE=worker
make docker-logs SERVICE=db
```

Equivalent raw commands:

```bash
docker compose logs -f --tail=100
docker compose logs -f --tail=100 api
```

## Inspect Logs And Data

Use Adminer at `http://localhost:8080` by default. Override `ADMINER_HOST_PORT` in `.env` if that host port is busy.

Important tables:

- `jobs`
- `trace_events`
- `agent_executions`
- `tool_calls`
- `eval_runs`
- `eval_case_results`
- `prompt_rewrite_proposals`
- `performance_deltas`

## Debug A Job

1. Run a streaming query.
2. Capture `job_id` from the SSE stream.
3. Call `GET /v1/jobs/{job_id}/trace`.
4. Inspect ordered trace events and tool calls.

## Debug Eval Regression

1. Call `GET /v1/evals/latest`.
2. Review category and dimension scores.
3. Inspect pending prompt rewrite proposal.
4. Approve or reject the rewrite.
5. Call `POST /v1/evals/targeted-rerun`.
6. Compare stored performance delta.

## Common Failure Scenarios

- Database unavailable: API startup or first request fails because PostgreSQL cannot be reached.
- Invalid request payload: API returns `VALIDATION_ERROR`.
- Unsafe code snippet: sandbox rejects input and logs `unsafe_input`.
- Empty tool result: orchestrator retries with a broader payload.
- Context overflow: budget manager logs a policy violation instead of silently truncating.
- Tool debugging: inspect `tool_calls.failure_mode`, `accepted`, and `rejection_reason`.

## Docker Troubleshooting

```bash
make compose-config
make docker-logs SERVICE=api
make docker-logs SERVICE=worker
make docker-down
make docker-up-build
```
