from __future__ import annotations

LOCAL_CHUNKS: list[dict[str, object]] = [
    {
        "chunk_id": "rag-001",
        "title": "Mega AI assignment objective",
        "source_url": "local://assignment/objective",
        "tags": ["assignment", "overview"],
        "content": (
            "The system must implement real-time multi-agent orchestration, dynamic tool "
            "selection, evaluation, adversarial robustness, and observable execution traces."
        ),
    },
    {
        "chunk_id": "rag-002",
        "title": "Orchestrator contract",
        "source_url": "local://assignment/orchestrator",
        "tags": ["orchestration", "agents"],
        "content": (
            "The master orchestrator decides which sub-agents to invoke, assigns context "
            "budgets, logs routing decisions, and mediates every handoff through shared context."
        ),
    },
    {
        "chunk_id": "rag-003",
        "title": "Critique and synthesis contract",
        "source_url": "local://assignment/critique-synthesis",
        "tags": ["critique", "synthesis"],
        "content": (
            "The critique agent scores individual claims and flags disagreed spans. The synthesis "
            "agent resolves contradictions and creates a provenance map per final sentence."
        ),
    },
    {
        "chunk_id": "rag-004",
        "title": "Tool failure contract",
        "source_url": "local://assignment/tools",
        "tags": ["tools", "failure"],
        "content": (
            "Every tool must define timeout, empty result, malformed input, unsafe input, and "
            "execution error behavior. Fallback logic must be implemented in code."
        ),
    },
    {
        "chunk_id": "rag-005",
        "title": "Evaluation contract",
        "source_url": "local://assignment/evaluation",
        "tags": ["evaluation", "adversarial"],
        "content": (
            "The evaluation harness has fifteen cases across straightforward, ambiguous, and "
            "adversarial categories. Scores include correctness, citation accuracy, contradiction "
            "resolution, tool efficiency, context compliance, and critique agreement."
        ),
    },
    {
        "chunk_id": "rag-006",
        "title": "Streaming and observability",
        "source_url": "local://assignment/streaming",
        "tags": ["sse", "observability"],
        "content": (
            "Agent output streams over Server-Sent Events. Trace logs include event order, "
            "agent ID, event type, input and output hashes, latency, token count, and policy violations."
        ),
    },
    {
        "chunk_id": "rag-007",
        "title": "Prompt improvement loop",
        "source_url": "local://assignment/prompt-loop",
        "tags": ["prompt", "eval"],
        "content": (
            "The meta-agent proposes prompt rewrites after eval failures. Rewrites are stored "
            "with structured diffs and require human approval before targeted re-evaluation."
        ),
    },
    {
        "chunk_id": "rag-008",
        "title": "Production constraints",
        "source_url": "local://assignment/production",
        "tags": ["production", "docker"],
        "content": (
            "Docker Compose must start the API server, background worker, PostgreSQL database, "
            "and lightweight log query interface using environment variables only."
        ),
    },
    {
        "chunk_id": "rag-009",
        "title": "Public API endpoint contract",
        "source_url": "local://assignment/api-endpoints",
        "tags": ["api", "endpoint", "endpoints", "route", "routes"],
        "content": (
            "The public API surface must expose exactly five /v1 endpoints: query streaming, "
            "job trace retrieval, latest eval summary, prompt rewrite decision, and targeted eval rerun."
        ),
    },
    {
        "chunk_id": "rag-010",
        "title": "Endpoint documentation and error contract",
        "source_url": "local://assignment/api-errors",
        "tags": ["api", "endpoint", "endpoints", "error", "documentation"],
        "content": (
            "No extra public API endpoints should be added. Error responses must include a "
            "machine-readable error_code, a human-readable message, and an optional job_id."
        ),
    },
]


STRUCTURED_RECORDS: list[dict[str, object]] = [
    {
        "record_key": "agent_count",
        "category": "assignment_metric",
        "value": "6",
        "metadata_json": {"meaning": "orchestrator plus five specialized agents"},
    },
    {
        "record_key": "required_endpoint_count",
        "category": "assignment_metric",
        "value": "5",
        "metadata_json": {"meaning": "exactly five public API endpoints"},
    },
    {
        "record_key": "eval_case_count",
        "category": "assignment_metric",
        "value": "15",
        "metadata_json": {"meaning": "five straightforward, five ambiguous, five adversarial"},
    },
    {
        "record_key": "required_tools",
        "category": "assignment_metric",
        "value": "web_search_stub,code_sandbox,data_lookup,self_reflection",
        "metadata_json": {"meaning": "four required tool interfaces"},
    },
]
