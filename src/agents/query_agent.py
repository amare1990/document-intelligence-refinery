"""
Query Interface Agent

Handles natural language queries over processed documents.

Implements three logical tools:
1. pageindex_navigate  – locate relevant sections
2. semantic_search     – retrieve LDUs via vector search
3. structured_query    – reserved for fact-table SQL queries

Returns a ProvenanceChain with full source traceability.
"""

"""
Query Interface Agent

Handles natural language queries over processed documents.

Tools:
1. pageindex_navigate  – locate relevant sections
2. semantic_search     – retrieve LDUs via vector search
3. structured_query    – SQL queries over fact tables

Returns a ProvenanceChain with full source traceability.
"""
# src/agents/query_agent.py

from typing import List, Tuple, Optional

from src.models.ldu import LDU
from src.models.provenance_chain import ProvenanceChain, ProvenanceStep
from src.adapters.embedding_store import LDUVectorStore
from src.adapters.fact_table_store import FactTableStore
from src.utils.page_index_lookup import load_page_index, find_relevant_sections
from src.agents.audit_agent import AuditAgent


class QueryAgent:
    """
    Stage 5 Query Interface Agent
    """

    def __init__(self, vector_store, fact_store=None):
        self.vector_store = vector_store
        self.fact_store = fact_store
        self.audit_agent = AuditAgent()

    # ------------------------------------------------
    # TOOL 1 — PageIndex Navigation
    # ------------------------------------------------

    def pageindex_navigate(self, doc_id: str, query: str) -> List[str]:
        """
        Traverse PageIndex tree to find relevant sections.
        """

        index = load_page_index(doc_id)

        if not index:
            return []

        return find_relevant_sections(index.root, query)

    # ------------------------------------------------
    # TOOL 2 — Semantic Search
    # ------------------------------------------------

    def semantic_search(self, query: str, top_k: int = 5) -> List[Tuple[LDU, float]]:
        """
        Retrieve semantically similar LDUs.
        """

        return self.vector_store.search(query, top_k)

    # ------------------------------------------------
    # TOOL 3 — Structured Query
    # ------------------------------------------------

    def structured_query(self, query: str):
        """
        Execute SQL queries against fact tables.
        """

        if not self.fact_store:
            return None

        return self.fact_store.query(query)

    # ------------------------------------------------
    # QUERY TYPE ROUTER
    # ------------------------------------------------

    def detect_query_type(self, question: str) -> str:
        """
        Simple heuristic routing.
        """

        numeric_keywords = [
            "total",
            "sum",
            "average",
            "count",
            "revenue",
            "amount",
            "table",
        ]

        if any(k in question.lower() for k in numeric_keywords):
            return "structured"

        return "semantic"

    # ------------------------------------------------
    # MAIN QUERY PIPELINE
    # ------------------------------------------------

    def query(self, doc_id: str, question: str, top_k: int = 5) -> ProvenanceChain:
        """
        Execute a document query with provenance tracking.
        """

        query_type = self.detect_query_type(question)

        # ----------------------------
        # Structured SQL Query
        # ----------------------------

        if query_type == "structured":
            result = self.structured_query(question)

            return ProvenanceChain(
                query=question,
                steps=[],
                overall_confidence=1.0 if result else 0.0,
            )

        # ----------------------------
        # Semantic Retrieval
        # ----------------------------

        sections = self.pageindex_navigate(doc_id, question)

        results = self.semantic_search(question, top_k)


        evidence_texts = [ldu.text for ldu, _ in results]

        audit_result = self.audit_agent.verify_claim(
            question,
            evidence_texts
        )


        steps: List[ProvenanceStep] = []

        for ldu, score in results:

            bbox = None
            if ldu.bbox:
                bbox = [ldu.bbox.x0, ldu.bbox.y0, ldu.bbox.x1, ldu.bbox.y1]

            step = ProvenanceStep(
                doc_id=ldu.doc_id,
                ldu_id=ldu.ldu_id,
                page_number=ldu.page_number,
                bbox=bbox,
                content_hash=ldu.content_hash,
                confidence=1 - score,
                section_path=ldu.section_path,
            )

            steps.append(step)

        overall_confidence = (
            sum(s.confidence for s in steps) / len(steps) if steps else 0
        )

        return ProvenanceChain(
            query=question,
            steps=steps,
            overall_confidence=overall_confidence,
            audit=audit_result
        )


