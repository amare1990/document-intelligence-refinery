""""
src/pipelines/run_extraction_batch.py
Responsibilities

load all .refinery/profiles/*.json

map each to its source file

call ExtractionRouter.route()

automatically write ledger entries (router already logs)
"""
from pathlib import Path
import json

from src.models.document_profile import DocumentProfile
from src.agents.extractor import ExtractionRouter

DATA_DIR = Path("data")
PROFILE_DIR = Path(".refinery/profiles")


def main():
    router = ExtractionRouter()

    for profile_file in PROFILE_DIR.glob("*.json"):
        profile_data = json.loads(profile_file.read_text())
        profile = DocumentProfile(**profile_data)

        source_path = DATA_DIR / f"{profile.doc_id}.pdf"

        if not source_path.exists():
            print(f"Missing file for {profile.doc_id}")
            continue

        router.route(str(source_path), profile)

    print("Batch extraction complete")


if __name__ == "__main__":
    main()
