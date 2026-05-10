# DESIGN.md

## Problem Framing

Mega AI asks for a production-minded multi-agent LLM system, not a simple chatbot. The core risk is that agent pipelines often hide brittle prompt behavior, weak tool failure handling, missing provenance, and non-reproducible evals. This project makes those behaviors explicit, persisted, and testable.

## Architecture

The system is a FastAPI backend with PostgreSQL as the source of truth. The streaming endpoint creates a job and the orchestrator drives the agent pipeline while emitting SSE events. Every important decision is also written to trace tables so a completed job can be reconstructed later.

Primary modules:

- `src/mega_ai/api`: exactly five public assignment endpoints
- `src/mega_ai/service`: job lifecycle, traces, evals, streaming wrappers, and prompt rewrites
- `src/mega_ai/agents`: decomposition, retrieval, critique, synthesis, compression, and meta-prompt agents
- `src/mega_ai/agents/orchestrator.py`: dynamic routing, handoffs, tool retries, and fallback decisions
- `src/mega_ai/core/context`: shared context and token budget management
- `src/mega_ai/tools`: explicit tool interfaces and failure contracts
- `src/mega_ai/evals`: cases, scorers, and diff logic
- `src/mega_ai/db/pgv`: SQLAlchemy models, Pydantic DB schemas, module-level CRUD, sessions, and seed data

## Agent Design And Decision Boundaries

Agents never call each other directly. They receive and update a `SharedContext` object, and the orchestrator mediates each handoff.

- Decomposition owns task breakdown and dependency graph.
- Retrieval owns multi-hop evidence collection and chunk citation.
- Critique owns claim-level review and span-level disagreement.
- Synthesis owns contradiction resolution and final provenance.
- Compression owns budget recovery while preserving structured state.
- Meta prompt owns rewrite proposals but cannot activate them.

## Shared Context Design

`SharedContext` stores job ID, normalized query, budgets, subtasks, agent outputs, tool results, retrieved chunks, critiques, routing decisions, policy violations, compressed notes, final answer, and sentence-level provenance.

This makes the system debuggable because agent state is not hidden in prompt-only memory.

## Tool Failure Contracts And Fallback Logic

Tools return a status, output payload, latency, and failure mode. Supported failure modes include timeout, empty result, malformed input, unsafe input, and execution error.

Fallbacks are implemented in `OrchestratorAgent._fallback_payload`, not in prompt text. Examples:

- empty result: broaden search query
- timeout: shrink input
- malformed data lookup: switch to safe endpoint-count lookup
- unsafe code: replace with a harmless rejection acknowledgement

## Context Budget Management

Each agent declares a maximum budget before execution. The budget manager estimates tokens, tracks used and remaining budget, and logs policy violations on overflow. Compression can run before synthesis when context grows beyond the synthesis budget.

Structured data such as tool outputs, scores, citations, dependency graphs, and provenance are preserved losslessly by the compression agent.

## Evaluation Design

The eval harness has 15 cases across straightforward, ambiguous, and adversarial categories. Scoring is implemented locally rather than delegated to a third-party eval framework.

Each case receives numeric and written scores for correctness, citation accuracy, contradiction resolution, tool efficiency, context compliance, and critique agreement.

## Self-Improving Prompt Loop

After an eval run, the system identifies the weakest scoring dimension and creates a prompt rewrite proposal. The proposal stores old prompt, new prompt, structured diff, target dimension, justification, and timestamp.

Rewrites are never auto-applied. A human must approve or reject through the prompt decision endpoint. Targeted re-eval then records performance delta.

## Observability And Tracing

Trace events include ordered event numbers, timestamp, job ID, agent ID, event type, input hash, output hash, latency, token count, policy violations, and event payload. Tool calls persist input hash, safe preview, output hash, retry number, status, failure mode, acceptance, and rejection reason.

The trace endpoint reconstructs the job sequence from persisted state.

## Failure Modes

Handled failure modes include malformed requests, missing jobs, tool timeouts, empty tool results, unsafe code, false-premise adversarial prompts, prompt injection attempts, context budget overflow, and failed pipeline execution.

## What Was Not Built

- No frontend.
- No live web search.
- No hardcoded provider credentials.
- No real paid LLM provider path.
- No Kubernetes or cloud deployment.
- No black-box eval framework.
- No arbitrary SQL generation.

These were intentionally omitted to keep the submission runnable and reviewable.

## Production Gap Analysis

Production hardening would require real provider adapters, provider-specific rate limits, stronger sandbox isolation, asynchronous job distribution, OpenTelemetry, migration management, row-level retention policies, tenant/user auth, secrets management, and CI-based regression snapshots.

## Scaling Story

FastAPI workers can scale horizontally behind a load balancer. PostgreSQL remains the audit source for jobs, traces, evals, and prompts. Long jobs should move to a distributed queue. SSE can be backed by pub/sub if workers are separated from API instances. Retrieval chunks can move to a vector database. Structured logs can move to a log backend. The same circuit-style fallback patterns used for tools can be extended to real LLM providers.
