# src/pipelines/run_layout_extraction.py
import sys
import json
from pathlib import Path

from src.agents.triage import TriageAgent
from src.strategies.layout_extractor import LayoutExtractor
from src.utils.ledger import log_entry


def main(pdf_path: str):
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        print(f"[ERROR] File not found: {pdf_file}")
        return

    # 1️⃣ Generate DocumentProfile via triage
    triage = TriageAgent()
    profile = triage.generate_profile(str(pdf_file))
    print(f"[INFO] Generated profile for {profile.doc_id}:\n{profile.model_dump_json(indent=2)}\n")

    # 2️⃣ Run LayoutExtractor
    extractor = LayoutExtractor()
    extracted = extractor.extract(str(pdf_file), profile)

    print(f"[INFO] Layout extraction result:\n{extracted.model_dump_json(indent=2)}\n")

    # 3️⃣ Log the extraction to ledger
    log_entry({
        "doc_id": profile.doc_id,
        "source_path": str(pdf_file),
        "strategy_used": extracted.strategy_used,
        "confidence_score": extracted.confidence,
        "estimated_extraction_cost": profile.estimated_extraction_cost,
        "processing_time_ms": 0,  # you can add timing if desired
    })

    print("[INFO] Ledger updated.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: uv run python -m src.pipelines.run_layout_extraction <path_to_pdf>")
    else:
        main(sys.argv[1])
