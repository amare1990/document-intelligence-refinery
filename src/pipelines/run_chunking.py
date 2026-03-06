""""
src/pipelines/run_chunking.py

This will read Stage 2 outputs from:

.refinery/extractions/*.json

Then generate LDUs.
"""

import argparse
import json
from pathlib import Path

from src.models.extracted_document import ExtractedDocument
from src.agents.semantic_chunker import SemanticChunker


EXTRACTION_DIR = Path(".refinery/extractions")
OUTPUT_DIR = Path(".refinery/ldus")


def process_extraction(file_path: Path):

    data = json.loads(file_path.read_text())
    extracted_doc = ExtractedDocument(**data)

    chunker = SemanticChunker()
    chunked = chunker.chunk(extracted_doc)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    out_path = OUTPUT_DIR / f"{chunked.doc_id}_ldus.json"

    out_path.write_text(chunked.model_dump_json(indent=2))

    print(f"[SAVED] {out_path}")


def main():

    parser = argparse.ArgumentParser(description="Run semantic chunking")

    parser.add_argument(
        "--extraction",
        help="Single extraction JSON file"
    )

    parser.add_argument(
        "--batch",
        action="store_true",
        help="Process all extraction files"
    )

    args = parser.parse_args()

    if args.extraction:
        process_extraction(Path(args.extraction))

    elif args.batch:
        for file in EXTRACTION_DIR.glob("*.json"):
            process_extraction(file)

    else:
        print("Provide --extraction or --batch")


if __name__ == "__main__":
    main()
