# src/pipelines/run_vision_extraction.py
import sys
from pathlib import Path
import time

from src.agents.triage import TriageAgent
from src.strategies.vision_extractor import VisionExtractor
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

    # 2️⃣ Run VisionExtractor
    extractor = VisionExtractor()
    start_time = time.time()
    extracted = extractor.extract(str(pdf_file), profile)
    elapsed_ms = int((time.time() - start_time) * 1000)

    print(f"[INFO] Vision extraction result:\n{extracted.model_dump_json(indent=2)}\n")

    # 3️⃣ Log the extraction to ledger
    log_entry({
        "doc_id": profile.doc_id,
        "source_path": str(pdf_file),
        "strategy_used": extracted.strategy_used,
        "confidence_score": extracted.confidence,
        "estimated_extraction_cost": profile.estimated_extraction_cost,
        "processing_time_ms": elapsed_ms,
    })

    print("[INFO] Ledger updated.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: uv run python -m src.pipelines.run_vision_extraction <path_to_pdf>")
    else:
        main(sys.argv[1])
