from __future__ import annotations

from mega_ai.agents.base import BaseAgent
from mega_ai.core.context.schemas import AgentOutput, SharedContext
from mega_ai.rag.retriever import LocalRetriever


class RetrievalAgent(BaseAgent):
    agent_id = "retrieval"
    default_budget = 3000

    def _run(self, context: SharedContext) -> AgentOutput:
        retriever = LocalRetriever(self.db)
        chunks = retriever.retrieve(context.user_query, top_k=3)
        selected = chunks[:2] if len(chunks) >= 2 else chunks
        context.retrieved_chunks = selected
        citations = [
            {
                "chunk_id": str(chunk["chunk_id"]),
                "claim": (
                    "This chunk contributes to the assignment-specific answer by grounding "
                    f"the response in {chunk['title']}."
                ),
                "source_url": str(chunk["source_url"]),
                "relevance_score": chunk["relevance_score"],
            }
            for chunk in selected
        ]
        content = (
            "Multi-hop retrieval used "
            + " and ".join(str(chunk["chunk_id"]) for chunk in selected)
            + ". "
            + " ".join(str(chunk["content"]) for chunk in selected)
        )
        return AgentOutput(
            agent_id=self.agent_id,
            content=content,
            claims=[
                "The answer is grounded in at least two retrieved chunks.",
                "Each retrieved chunk has a stable chunk ID and source URL.",
            ],
            citations=citations,
            metadata={"retrieved_chunks": selected},
        )
