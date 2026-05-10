# API Documentation

The app exposes exactly five public `/v1` endpoints.

## POST /v1/query/stream

Submit a query and receive Server-Sent Events.

Request:

```json
{
  "query": "Explain the orchestrator behavior with sources.",
  "metadata": {}
}
```

Events include `job_started`, `orchestrator_decision`, `agent_started`, `agent_token`, `tool_call_started`, `tool_call_finished`, `tool_output_rejected`, `context_budget_update`, `agent_finished`, `final_answer`, `job_finished`, and `job_failed`.

## GET /v1/jobs/{job_id}/trace

Returns the full execution trace for a job ID.

Response includes:

- job status and final answer
- ordered trace events
- agent executions and prompt versions
- tool calls and acceptance/rejection status
- provenance map

## GET /v1/evals/latest

Returns the latest eval run summary. If no eval exists, the system runs the deterministic 15-case harness.

Response includes:

- category summaries
- dimension summaries
- pass count
- average score
- pending prompt rewrite proposals

## POST /v1/prompts/rewrites/{rewrite_id}/decision

Approve or reject a pending prompt rewrite.

Request:

```json
{
  "decision": "approve",
  "reviewer_note": "Accept for targeted re-eval."
}
```

## POST /v1/evals/targeted-rerun

Run targeted re-eval on failed cases from the latest eval or a specified eval.

Request:

```json
{
  "eval_run_id": "optional-eval-run-id"
}
```

## Error Format

```json
{
  "error_code": "MACHINE_READABLE_CODE",
  "message": "Human readable message",
  "job_id": "optional-job-id"
}
```
