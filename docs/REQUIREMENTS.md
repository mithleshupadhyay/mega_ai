# Requirements Mapping

| Assignment requirement | Implementation |
| --- | --- |
| Dynamic multi-agent orchestration | `OrchestratorAgent._routing_decision` selects agents/tools and logs routing decisions; agents communicate through `SharedContext`. |
| Decomposition agent | `src/mega_ai/agents/decomposition.py` creates typed subtasks with dependencies. |
| Multi-hop retrieval | `src/mega_ai/agents/retrieval.py` retrieves and cites at least two chunks from `RetrievedChunk`. |
| Critique agent | `src/mega_ai/agents/critique.py` scores claims and flags disagreed spans. |
| Synthesis agent | `src/mega_ai/agents/synthesis.py` resolves critique disagreements and writes sentence provenance. |
| Shared context | `src/mega_ai/core/context/schemas.py` defines `SharedContext`. |
| Four tools | `src/mega_ai/tools/web_search_stub.py`, `code_sandbox.py`, `data_lookup.py`, `self_reflection.py`. |
| Tool failure contracts | Tools return explicit `failure_mode`; fallback is in `OrchestratorAgent._fallback_payload`. |
| Context budget manager | `src/mega_ai/core/context/budget_manager.py`. |
| Compression agent | `src/mega_ai/agents/compression.py`. |
| 15-case eval harness | `src/mega_ai/evals/cases.py`. |
| Local scoring logic | `src/mega_ai/evals/scorers.py`. |
| Reproducible eval persistence | `EvalRun` and `EvalCaseResult` tables. |
| Self-improving prompt loop | `PromptRewriteService` and `MetaPromptAgent`. |
| Human approval/rejection | `POST /v1/prompts/rewrites/{rewrite_id}/decision`. |
| Targeted re-eval | `POST /v1/evals/targeted-rerun`. |
| SSE streaming | `POST /v1/query/stream`. |
| Full trace endpoint | `GET /v1/jobs/{job_id}/trace`. |
| Exactly five endpoints | FastAPI docs/OpenAPI disabled; only five `/v1` routes are registered. |
| Docker Compose services | API, worker, PostgreSQL, Adminer log query interface. |
| No credentials hardcoded | `.env.example` only; no `.env` committed. |
