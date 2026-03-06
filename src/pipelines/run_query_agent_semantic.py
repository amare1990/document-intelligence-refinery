# src/pipelines/run_query_agent_semantic.py

import argparse
from pathlib import Path
import json

from src.agents.query_agent import SemanticQueryAgent
from src.adapters.embedding_store import LDUVectorStore
from src.utils.ldu_loader import load_ldus


def main():
    parser = argparse.ArgumentParser(
        description="Stage 5: Semantic Query + Provenance Agent"
    )

    parser.add_argument(
        "--query",
        required=True,
        type=str,
        help="Query text"
    )

    parser.add_argument(
        "--ldus-dir",
        default=".refinery/ldus",
        type=str
    )

    parser.add_argument(
        "--pageindex-dir",
        default=".refinery/pageindex",
        type=str
    )

    parser.add_argument(
        "--openai-api-key",
        required=True
    )

    parser.add_argument(
        "--top-k",
        default=5,
        type=int
    )

    args = parser.parse_args()

    ldus_path = Path(args.ldus_dir)
    pageindex_path = Path(args.pageindex_dir)

    if not ldus_path.exists():
        print(f"[!] LDUs folder missing: {ldus_path}")
        return

    print("[*] Loading LDUs...")
    ldus = load_ldus(ldus_path)

    print("[*] Building vector store...")
    store = LDUVectorStore(api_key=args.openai_api_key)

    store.add_ldus(ldus)

    print("[*] Initializing SemanticQueryAgent...")
    agent = SemanticQueryAgent(
        store=store
    )

    print(f"[*] Running query: {args.query}")

    provenance_chain = agent.query(args.query, top_k=args.top_k)

    print("\nProvenance Steps:")
    for step in provenance_chain.steps:
        section = " > ".join(step.section_path) if step.section_path else "N/A"

        print(
            f"Doc={step.doc_id} "
            f"Page={step.page_number} "
            f"Section={section} "
            f"Confidence={step.confidence:.2f}"
        )

    print(f"\nOverall Confidence: {provenance_chain.overall_confidence:.2f}")

    output_file = Path(".refinery") / "provenance_result.json"

    with open(output_file, "w") as f:
        json.dump(provenance_chain.model_dump(), f, indent=2)

    print(f"[SAVED] {output_file}")


if __name__ == "__main__":
    main()
