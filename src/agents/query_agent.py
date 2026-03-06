"""
This module defines the QueryAgent class, which is responsible for handling user queries and
generating provenance chains based on the results retrieved from the vector store.
The QueryAgent class interacts with the VectorStore to search for relevant LDUs based on the user's query
and constructs a ProvenanceChain that captures the steps taken to arrive at the answer. Each step in the
provenance chain includes information about the document ID, LDU ID, page number, content hash, and confidence score.
The overall confidence of the provenance chain is also calculated based on the individual steps.
The QueryAgent class serves as a crucial component in the system for managing and retrieving document content,
providing a structured way to trace the origins of the information used to answer user queries.
The implementation assumes that the ProvenanceChain and ProvenanceStep classes are defined in
the src.models.provenance_chain module, and that the VectorStore class is defined in the src.adapters.vector_store module.
The QueryAgent class can be extended with additional functionality such as error handling, logging, and support
for more complex query processing as needed. The provided code is a basic implementation and can be modified to
fit specific use cases or requirements of the application.
"""
# src/agents/query_agent.py

from typing import List

from src.models.provenance_chain import ProvenanceChain, ProvenanceStep
from src.adapters.embedding_store import LDUVectorStore
from src.utils.page_index_lookup import load_page_index, find_section


class SemanticQueryAgent:

    def __init__(self, store: LDUVectorStore):
        self.store = store

    def query(self, question: str, top_k: int = 5) -> ProvenanceChain:

        results = self.store.search(question, top_k)

        steps: List[ProvenanceStep] = []

        for ldu, score in results:

            section_path = []

            index = load_page_index(ldu.doc_id)

            if index:
                section_path = find_section(index.root, ldu.page_number, [])

            step = ProvenanceStep(
                doc_id=ldu.doc_id,
                ldu_id=ldu.ldu_id,
                page_number=ldu.page_number,
                content_hash=ldu.content_hash,
                confidence=1 - score,
                section_path=section_path,
            )

            steps.append(step)

        confidence = sum(s.confidence for s in steps) / len(steps) if steps else 0

        return ProvenanceChain(
            query=question,
            steps=steps,
            overall_confidence=confidence,
        )
