# Triage Batch Runner: Processes all PDFs in the data/ directory to generate profiles for each document.
# This is the first stage of the pipeline, responsible for analyzing documents and creating profiles that will
import argparse
from pathlib import Path

from src.agents.triage import TriageAgent


def main():
    parser = argparse.ArgumentParser(description="Run Stage-1 Triage")
    parser.add_argument(
        "input",
        nargs="?",
        help="Optional single PDF path. If omitted, processes entire data/ directory.",
    )
    parser.add_argument(
        "--data-dir",
        default="data",
        help="Directory for batch mode (default: data/)",
    )

    args = parser.parse_args()

    triage = TriageAgent()

    # -------------------------
    # SINGLE FILE MODE
    # -------------------------
    if args.input:
        pdf_path = Path(args.input)

        if not pdf_path.exists():
            print(f"File not found: {pdf_path}")
            return

        profile = triage.generate_profile(str(pdf_path))
        print(f"✓ Profile created: {profile.doc_id}")
        return

    # -------------------------
    # BATCH MODE
    # -------------------------
    data_dir = Path(args.data_dir)
    pdfs = list(data_dir.glob("*.pdf"))

    for pdf_path in pdfs:
        profile = triage.generate_profile(str(pdf_path))
        print(f"✓ Profile created: {profile.doc_id}")

    print("Batch triage complete")


if __name__ == "__main__":
    main()
