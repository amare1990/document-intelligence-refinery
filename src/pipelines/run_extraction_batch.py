# src/pipelines/run_extraction_batch.py
from pathlib import Path
import argparse

from src.agents.triage import TriageAgent
from src.agents.extractor import ExtractionRouter

DATA_DIR = Path("data")


def process_pdf(pdf_file: Path, triage: TriageAgent, router: ExtractionRouter):
    """Process a single PDF through triage and extraction."""
    if not pdf_file.exists():
        print(f"[ERROR] File not found: {pdf_file}")
        return

    print(f"[INFO] Processing: {pdf_file}")

    # 1️⃣ Generate DocumentProfile
    profile = triage.generate_profile(str(pdf_file))
    print(f"[INFO] Generated profile for {profile.doc_id}:\n{profile.model_dump_json(indent=2)}\n")

    # 2️⃣ Route through extraction
    extracted = router.route(str(pdf_file), profile)

    print(f"[INFO] Extraction complete")
    print(f"Strategy: {extracted.strategy_used}")
    print(f"Confidence: {extracted.confidence}")
    print(f"LDU count: {len(extracted.ldus)}\n")


def main():
    parser = argparse.ArgumentParser(description="Batch or single PDF extraction")
    parser.add_argument(
        "pdf_path",
        nargs="?",
        default=None,
        help="Path to a single PDF file (optional). If omitted, batch mode runs on all PDFs in 'data/'",
    )
    args = parser.parse_args()

    triage = TriageAgent()
    router = ExtractionRouter()

    if args.pdf_path:
        pdf_file = Path(args.pdf_path)
        process_pdf(pdf_file, triage, router)
    else:
        # Batch mode: all PDFs in DATA_DIR
        pdf_files = list(DATA_DIR.glob("*.pdf"))
        if not pdf_files:
            print(f"[WARN] No PDF files found in {DATA_DIR}")
            return

        for pdf_file in pdf_files:
            process_pdf(pdf_file, triage, router)

    print("[INFO] Extraction complete.")


if __name__ == "__main__":
    main()
