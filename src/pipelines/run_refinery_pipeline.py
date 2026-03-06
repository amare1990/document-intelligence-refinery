"""
Master Refinery Pipeline

Runs the complete Document Intelligence Refinery:

PDF
 → Stage 1: Triage (DocumentProfile)
 → Stage 2: Extraction
 → Stage 3: Semantic Chunking (LDUs)
 → Stage 4: PageIndex Builder
 → Stage 5: Vector Embedding
 → Stage 6: Query + Provenance
"""

import argparse
import json
from pathlib import Path

from src.agents.triage import TriageAgent
from src.agents.extractor import ExtractionRouter
from src.agents.semantic_chunker import SemanticChunker
from src.agents.page_index_builder import PageIndexBuilder
from src.agents.query_agent import SemanticQueryAgent

from src.adapters.embedding_store import LDUVectorStore

from src.models.extracted_document import ExtractedDocument


REFINERY = Path(".refinery")
LDUS_DIR = REFINERY / "ldus"
EXTRACTIONS_DIR = REFINERY / "extractions"
PAGEINDEX_DIR = REFINERY / "page_index"


def ensure_dirs():
    """Create refinery folders if missing."""
    for d in [
        REFINERY / "profiles",
        EXTRACTIONS_DIR,
        LDUS_DIR,
        PAGEINDEX_DIR,
        REFINERY / "vector_store",
    ]:
        d.mkdir(parents=True, exist_ok=True)


def run_pipeline(pdf_path: str, query: str | None = None):

    ensure_dirs()

    print("\n==============================")
    print("Document Intelligence Refinery")
    print("==============================")

    # ---------------------------------------------------
    # Stage 1 — TRIAGE
    # ---------------------------------------------------

    print("\n[Stage 1] Document Profiling")

    triage = TriageAgent()
    profile = triage.generate_profile(pdf_path)

    print(f"DocID: {profile.doc_id}")
    print(f"Origin: {profile.origin_type}")
    print(f"Layout: {profile.layout_complexity}")

    # ---------------------------------------------------
    # Stage 2 — EXTRACTION
    # ---------------------------------------------------

    print("\n[Stage 2] Extraction")

    router = ExtractionRouter()
    extracted: ExtractedDocument = router.route(pdf_path, profile)

    extraction_file = EXTRACTIONS_DIR / f"{profile.doc_id}.json"

    with open(extraction_file, "w", encoding="utf-8") as f:
        json.dump(extracted.model_dump(), f, indent=2)

    print(f"Strategy used: {extracted.strategy_used}")
    print(f"Saved extraction → {extraction_file}")

    # ---------------------------------------------------
    # Stage 3 — SEMANTIC CHUNKING
    # ---------------------------------------------------

    print("\n[Stage 3] Semantic Chunking")

    chunker = SemanticChunker()
    enriched = chunker.chunk(extracted)

    ldu_file = LDUS_DIR / f"{profile.doc_id}.json"

    with open(ldu_file, "w", encoding="utf-8") as f:
        json.dump([ldu.model_dump() for ldu in enriched.ldus], f, indent=2)

    print(f"LDUs generated: {len(enriched.ldus)}")
    print(f"Saved LDUs → {ldu_file}")

    # ---------------------------------------------------
    # Stage 4 — PAGE INDEX
    # ---------------------------------------------------

    print("\n[Stage 4] PageIndex Builder")

    index_builder = PageIndexBuilder()
    page_index = index_builder.build(enriched)

    index_file = PAGEINDEX_DIR / f"{profile.doc_id}.json"

    with open(index_file, "w", encoding="utf-8") as f:
        json.dump(page_index.model_dump(), f, indent=2)

    print(f"PageIndex saved → {index_file}")

    # ---------------------------------------------------
    # Stage 5 — VECTOR STORE
    # ---------------------------------------------------

    print("\n[Stage 5] Vector Embedding")

    store = LDUVectorStore()

    store.add_ldus(enriched.ldus)

    print("Vector index updated")

    # ---------------------------------------------------
    # Stage 6 — QUERY
    # ---------------------------------------------------

    if query:

        print("\n[Stage 6] Semantic Query")

        agent = SemanticQueryAgent(store)

        result = agent.query(query)

        print("\nQuery:", query)
        print("\nProvenance:")

        for step in result.steps:

            section = " > ".join(step.section_path) if step.section_path else "N/A"

            print(
                f"Doc:{step.doc_id} | Page:{step.page_number} | Section:{section} | LDU:{step.ldu_id}"
            )

        print("\nConfidence:", result.overall_confidence)


def main():

    parser = argparse.ArgumentParser(description="Run full Document Intelligence Refinery")

    parser.add_argument(
        "--pdf",
        required=True,
        help="PDF document to process"
    )

    parser.add_argument(
        "--query",
        required=False,
        help="Optional semantic query"
    )

    args = parser.parse_args()

    run_pipeline(args.pdf, args.query)


if __name__ == "__main__":
    main()
