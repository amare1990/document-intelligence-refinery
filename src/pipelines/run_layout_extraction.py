# src/pipelines/run_layout_extraction.py

import sys
import time
from pathlib import Path

from src.agents.triage import TriageAgent
from src.strategies.layout_extractor import LayoutExtractor
from src.utils.ledger import log_entry


def main(pdf_path: str):

    pdf_file = Path(pdf_path).resolve()

    if not pdf_file.exists():
        print(f"[ERROR] File not found: {pdf_file}")
        sys.exit(1)

    print(f"[INFO] Processing: {pdf_file}")

    # -----------------------------
    # 1️⃣ TRIAGE PHASE
    # -----------------------------

    triage = TriageAgent()

    profile = triage.generate_profile(str(pdf_file))

    print(
        f"\n[INFO] Generated DocumentProfile:\n"
        f"{profile.model_dump_json(indent=2)}\n"
    )

    # -----------------------------
    # 2️⃣ EXTRACTION PHASE
    # -----------------------------

    extractor = LayoutExtractor()

    start_time = time.time()

    try:
        extracted = extractor.extract(str(pdf_file), profile)
    except Exception as e:
        print(f"[ERROR] Layout extraction failed: {e}")
        sys.exit(1)

    elapsed_ms = int((time.time() - start_time) * 1000)

    # -----------------------------
    # 3️⃣ RESULT SUMMARY
    # -----------------------------

    ldu_count = len(extracted.ldus)

    print(
        f"[INFO] Extraction complete\n"
        f"Strategy: {extracted.strategy_used}\n"
        f"Confidence: {extracted.confidence}\n"
        f"LDU count: {ldu_count}\n"
        f"Processing time: {elapsed_ms} ms\n"
    )

    # Optional: print full object
    print(
        f"[DEBUG] ExtractedDocument:\n"
        f"{extracted.model_dump_json(indent=2)}\n"
    )

    # -----------------------------
    # 4️⃣ LEDGER LOGGING
    # -----------------------------

    log_entry(
        {
            "doc_id": profile.doc_id,
            "source_path": str(pdf_file),
            "strategy_used": extracted.strategy_used,
            "confidence_score": extracted.confidence,
            "estimated_extraction_cost": profile.estimated_extraction_cost,
            "ldu_count": ldu_count,
            "processing_time_ms": elapsed_ms,
        }
    )

    print("[INFO] Ledger updated.")


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print(
            "Usage:\n"
            "uv run python -m src.pipelines.run_layout_extraction <path_to_pdf>"
        )
        sys.exit(1)

    main(sys.argv[1])
