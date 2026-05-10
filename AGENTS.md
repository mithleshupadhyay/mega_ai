# AGENTS.md instructions for /home/rudra/Documents/mega_ai

## Project context

This repository contains the Mega AI LLM Engineer take-home assignment: a real-time multi-agent LLM orchestration and evaluation system.

Mega AI builds AI agents that execute real workflows inside software. The assignment should therefore feel like a practical backend system, not a toy demo or a prompt-only prototype.

Use Python, FastAPI, PostgreSQL, Pydantic, SQLAlchemy, Server-Sent Events, Docker Compose, deterministic local agent behavior, and mock-driven tests. Do not use LangChain, LangGraph, LiteLLM-style gateways, or third-party eval frameworks as black boxes for the core implementation.

The reviewer should be able to clone the repo, run it quickly, inspect the architecture, understand the agent decisions, run evals, and see persisted traces without paid LLM keys.

## Reference style

Use the production-style structure already present in this repository:

- thin FastAPI routers in `src/mega_ai/api`
- business workflows in `src/mega_ai/service`
- deterministic agent implementations in `src/mega_ai/agents`
- explicit tool interfaces in `src/mega_ai/tools`
- SQLAlchemy models in `src/mega_ai/db/pgv/models`
- Pydantic DB schemas in `src/mega_ai/db/pgv/schemas`
- module-level CRUD functions in `src/mega_ai/db/pgv/crud`
- tests grouped by unit/integration and by module boundary

## Repository layout

Keep one repo. Main source code must live under `src/mega_ai`.

Use this structure as the target shape:

```text
src/mega_ai/
  api/
  agents/
  core/
    config.py
    context/
    logging/
    tasks/
  db/
    pgv/
      crud/
      models/
      schemas/
      db.py
  evals/
  rag/
  security/
  service/
  tools/
  main.py
tests/
  unit/
    apis/
    db/
      pgv/
        crud/
        schemas/
    service/
    agents/
    tools/
    evals/
  integration/
    apis/
docs/
alembic/
scripts/
```

Mapping from the assignment wording to this repo style:

- `src/config` means `src/mega_ai/core/config.py`
- `src/context` means `src/mega_ai/core/context`
- `src/logging` means `src/mega_ai/core/logging`
- `src/services` means `src/mega_ai/service`
- `src/worker` means `src/mega_ai/core/tasks` plus root `worker.py`
- `src/db` means `src/mega_ai/db/pgv`

Do not create parallel top-level packages that duplicate these locations.

## Backend coding style

Follow the repository service style:

- Use snake_case file names and clear domain module names.
- Keep FastAPI route handlers in `api/` thin.
- Put business logic in `service/`, `agents/`, `tools/`, `evals/`, `rag/`, and `db/pgv/crud/`.
- Use module-level CRUD functions in `db/pgv/crud/<domain>.py`, not large generic repository abstractions.
- Use SQLAlchemy declarative models in `db/pgv/models/<domain>.py`.
- Use Pydantic schemas in `db/pgv/schemas/<domain>.py` for domain and DB-facing request/response models.
- Keep `api/schemas.py` only for small API wrapper schemas if needed.
- Use `ThingBase`, `ThingCreate`, `ThingUpdate`, `ThingOut` naming where it fits.
- Use `ConfigDict(from_attributes=True)` for Pydantic output schemas backed by SQLAlchemy models.
- Use explicit SQLAlchemy columns, indexes, relationships, and JSON/JSONB compatibility helpers.
- Keep `created_at`, `updated_at`, status fields, and IDs explicit on persisted workflow models.
- Prefer `Session` dependency injection through `get_db`.
- Keep DB commits/rollbacks explicit inside CRUD or service functions.
- Keep tests close to the module shape, like `tests/unit/db/pgv/crud/test_<domain>.py` and `tests/unit/apis/test_<domain>_api.py`.

The code should be simple and inspectable. Add abstractions only when they reduce real repetition or clarify the assignment behavior.

## Core rules

- Keep exactly five public `/v1` endpoints.
- Do not add extra public endpoints, including health/debug/admin endpoints, unless explicitly asked.
- Do not add a frontend.
- Do not add real user auth, Kubernetes, cloud deployment, admin dashboards, or unrelated extras.
- Persist jobs, traces, agent executions, tool calls, eval runs, scores, prompt versions, prompt rewrite proposals, rewrite decisions, and performance deltas.
- All inter-agent communication must go through `SharedContext`.
- Agents must not call each other directly.
- The orchestrator mediates all handoffs.
- Fallback logic must be explicit in Python code, not hidden inside prompts.
- Keep tests deterministic and runnable without paid LLM keys.
- Do not commit `.env` or secrets.
- Do not push to GitHub unless explicitly asked.

## Public API contract

Expose exactly these five public endpoints:

- `POST /v1/query/stream`
- `GET /v1/jobs/{job_id}/trace`
- `GET /v1/evals/latest`
- `POST /v1/prompts/rewrites/{rewrite_id}/decision`
- `POST /v1/evals/targeted-rerun`

All endpoints must be documented in README/docs. Route handlers should only validate inputs, call services, and return responses.

Error responses must use this format:

```json
{
  "error_code": "MACHINE_READABLE_CODE",
  "message": "Human readable message",
  "job_id": "optional-job-id-if-applicable"
}
```

Do not expose FastAPI docs as a workaround for missing documentation unless explicitly requested. Document the API in `docs/` and `README.md`.

## Required agents

Implement these agents under `src/mega_ai/agents`:

- `orchestrator.py`
- `decomposition.py`
- `retrieval.py`
- `critique.py`
- `synthesis.py`
- `compression.py`
- `meta_prompt.py`
- `base.py`
- `prompts.py`

The master orchestrator must dynamically decide at runtime:

- which agents to invoke
- agent order
- context budget per agent
- which tools to call
- whether dependencies are satisfied
- whether compression is required
- how to handle insufficient tool results

The orchestrator must not be a hardcoded fixed chain. It may use deterministic local heuristics for this assignment, but the decision must be structured, query-dependent, persisted, and logged with justification.

Every agent must declare a maximum context budget before execution. Agent output must be written into `SharedContext`; do not pass one agent object into another agent.

## Agent behavior requirements

Decomposition agent:

- Break ambiguous or underspecified queries into typed subtasks.
- Include dependency graph data.
- Mark dependency status clearly.
- Do not allow dependent subtasks to execute before dependencies resolve.

Retrieval agent:

- Perform multi-hop retrieval across at least two chunks when retrieval is needed.
- Cite chunk IDs and explain which chunk contributed to which answer part.
- Use local corpus and deterministic retrieval logic.

Critique agent:

- Review every other agent output.
- Extract claims.
- Assign confidence per claim.
- Flag exact disagreed spans, not only whole-output judgments.
- Produce structured critique objects.

Synthesis agent:

- Merge agent outputs.
- Resolve critique contradictions.
- Avoid surfacing unresolved contradictions to the user.
- Return final answer with provenance per sentence.

Compression agent:

- Run when context budget is exceeded or about to exceed budget.
- Preserve structured data losslessly: tool outputs, scores, citations, IDs, budgets, policy violations.
- Compress only conversational filler or redundant natural language.

Meta-prompt agent:

- Inspect failed eval cases after eval runs.
- Identify the worst-performing prompt by scoring dimension.
- Propose a prompt rewrite with structured diff and justification.
- Store the proposal.
- Never auto-apply prompt rewrites.

## Tool requirements

Implement real tool interfaces under `src/mega_ai/tools`:

- `web_search_stub.py`
- `code_sandbox.py`
- `data_lookup.py`
- `self_reflection.py`
- `base.py`

Every tool must return a structured response containing:

- tool name
- status
- output payload
- latency
- failure mode if any
- accepted/rejected flag
- rejection reason if rejected
- metadata if useful

Every tool must define behavior for:

- timeout
- empty result
- malformed input
- unsafe input
- execution error

Required tools:

- Web search stub returning structured results with URLs and relevance scores.
- Python code execution sandbox returning stdout, stderr, exit code, timeout, and latency.
- Structured data lookup tool that converts natural language to safe SQL over local PostgreSQL data.
- Self-reflection tool that rereads previous outputs in the same session and identifies contradictions.

Agents may retry insufficient tool results up to two times. Each retry must be logged separately with retry number and modified input.

Tool call logging must include:

- input hash
- safe input preview if allowed
- output hash
- latency
- retry number
- status
- failure mode
- whether the agent accepted or rejected the result

## Context-window management

Use `src/mega_ai/core/context` for:

- `SharedContext`
- context budget models
- provenance models
- token usage tracking

Track token usage per:

- agent
- turn
- tool result
- retrieved chunk
- compressed context
- final output

Agents must be able to check remaining budget before adding context.

If context exceeds budget:

- run compression where possible
- log a policy violation if an agent overflows budget
- do not silently truncate

Policy violations must be persisted and visible in trace output.

## Persistence and observability

Use SQLAlchemy models under `db/pgv/models` for:

- jobs
- trace events
- agent executions
- tool calls
- knowledge chunks
- eval runs
- eval case results
- prompt versions
- prompt rewrite proposals
- rewrite decisions
- performance deltas

Use module-level CRUD functions under `db/pgv/crud`.

Structured trace events must include:

- timestamp
- job ID
- agent ID when applicable
- event type
- input hash
- output hash
- latency
- token count
- policy violations
- structured payload

Persist logs/traces to the database. Console logging is useful but not sufficient.

`GET /v1/jobs/{job_id}/trace` must reconstruct the exact sequence of:

- orchestrator decisions
- agent starts/finishes
- tool calls
- retries
- context budget updates
- handoffs
- final answer

## Streaming

`POST /v1/query/stream` must stream Server-Sent Events.

The stream should expose:

- job started
- orchestrator decision
- current agent
- token-level or small chunk output
- tool call started
- tool call finished
- tool output accepted/rejected
- context budget remaining
- policy violations
- final answer
- job finished or failed

Use deterministic local output generation for tests. Do not rely on external LLM calls for core behavior.

## Evaluation harness

Build the eval system under `src/mega_ai/evals`.

Include exactly 15 local test cases:

- 5 straightforward known-answer cases
- 5 ambiguous or underspecified cases
- 5 adversarial cases

Adversarial cases must include:

- prompt injection
- wrong premises
- contradiction-inducing queries
- cases requiring critique/synthesis conflict resolution

Scoring dimensions:

- answer correctness
- citation accuracy
- contradiction resolution quality
- tool selection efficiency
- context budget compliance
- critique agreement rate with final output

Each score must include:

- numeric value
- written justification

Do not use a third-party eval framework as a black box.

Persist every eval run with:

- exact prompts sent to each agent
- exact tool calls
- exact agent outputs
- scores
- justifications
- timestamps
- prompt version IDs
- diffable output snapshot

Re-running evals on the same inputs should produce diff-able output for regression review.

## Self-improving prompt loop

After each eval run:

- the meta-prompt agent must inspect failed cases
- identify the worst-performing prompt by dimension
- propose a rewritten prompt
- include structured diff and justification
- store the proposal
- do not apply it automatically

Add human approval/rejection flow through:

`POST /v1/prompts/rewrites/{rewrite_id}/decision`

If approved:

- allow targeted re-eval only on previously failed cases
- store approval timestamp
- store performance delta
- keep the loop auditable end to end

If rejected:

- store rejection timestamp and reviewer note
- do not activate the rewrite

## RAG and local data

Use `src/mega_ai/rag` for:

- local corpus
- chunking
- retrieval
- citation logic

Chunk IDs must be stable. Retrieval must be deterministic. Citation output must connect answer spans or sentences back to chunk IDs.

Use `src/mega_ai/db/pgv/crud/seeds.py` or equivalent seed helpers for local deterministic data needed by the structured data lookup tool and eval cases.

## Security and safety

For the code sandbox:

- reject unsafe imports and unsafe filesystem/process/network operations
- enforce timeout
- capture stdout and stderr
- return exit code, timeout flag, latency, and failure mode
- do not execute shell commands from user input

For SQL lookup:

- only allow safe read-only SELECT queries
- use a controlled natural-language-to-SQL mapping or whitelist
- reject unsafe input such as write operations, stacked statements, comments used for injection, or unknown tables
- never concatenate untrusted input into SQL directly

For logs:

- redact secrets
- store hashes for full inputs/outputs where raw values are risky
- store safe previews only when allowed

## Documentation requirements

The repository must include:

- README with five-minute setup instructions
- architecture diagram as text or image
- API documentation for the exact five endpoints
- description of every agent and decision boundaries
- tool failure contracts
- eval design and scoring dimensions
- self-improving prompt loop explanation
- observability and trace reconstruction explanation
- known limitations with honest assessment
- what to build next
- AI-collaboration attestation describing where AI assistants were used

Keep docs assignment-focused. Do not add marketing copy or unrelated product material.

## Docker and local setup

Docker Compose must start:

- API server
- background worker
- PostgreSQL
- lightweight log query interface such as Adminer

Environment variables must be the only configuration mechanism. No credentials may be hardcoded.

Keep `.env.example` complete and safe. Do not commit `.env`.

## Testing rules

Tests must be deterministic and mock-driven.

Cover at least:

- API contract and exact endpoint set
- error response format
- orchestrator routing decisions
- SharedContext communication
- no direct agent-to-agent calls
- context budget overflow and compression
- tool failure contracts
- tool retry logging
- retrieval citations across at least two chunks
- critique span disagreement
- synthesis provenance per sentence
- 15-case eval harness
- prompt rewrite approval/rejection
- targeted failed-case re-eval
- trace reconstruction order

Use this test layout:

- `tests/unit/apis/test_<domain>_api.py`
- `tests/unit/db/pgv/crud/test_<domain>.py`
- `tests/unit/db/pgv/schemas/test_<domain>.py`
- `tests/unit/service/test_<domain>_service.py`
- `tests/unit/agents/test_<agent>.py`
- `tests/unit/tools/test_<tool>.py`
- `tests/integration/apis/test_<flow>.py`

## Verification before finishing

Run:

```bash
poetry run pytest
poetry run ruff check .
poetry run mypy src
docker compose config
```

Also check:

```bash
poetry run python - <<'PY'
from mega_ai.main import app
print(sorted(route.path for route in app.routes if route.path.startswith("/v1/")))
PY
rg -n 'LangChain|LangGraph|litellm|LiteLLM' src tests docs README.md pyproject.toml
git status --short
```

The first command should confirm only the five allowed public `/v1` endpoints. The second command should not show forbidden core-framework usage, except where documentation explicitly says not to use those tools.

If a verification command cannot be run, state why in the final response.

## Done criteria

Work is done only when:

- the exact five endpoints exist
- route handlers are thin
- all required agents exist and use `SharedContext`
- orchestrator decisions are dynamic and logged
- all four tools have explicit failure contracts
- retries and fallback logic are visible in code
- context budget tracking and compression are implemented
- traces are persisted and reconstructable
- eval harness has 15 cases with multidimensional scoring
- prompt rewrite loop stores proposals and requires human decision
- Docker Compose is valid
- tests, ruff, mypy, and compose config pass or failures are clearly reported
- README/docs explain setup, architecture, agents, evals, limitations, and AI collaboration
