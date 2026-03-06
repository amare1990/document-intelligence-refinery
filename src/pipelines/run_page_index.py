
import json
import argparse
from pathlib import Path

from src.models.extracted_document import ExtractedDocument
from src.agents.page_index_builder import PageIndexBuilder


INPUT_DIR = Path(".refinery/ldus")
OUTPUT_DIR = Path(".refinery/page_index")


def process_file(file):

    data = json.loads(file.read_text())
    doc = ExtractedDocument(**data)

    builder = PageIndexBuilder()
    index = builder.build(doc)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    out = OUTPUT_DIR / f"{doc.doc_id}_index.json"

    out.write_text(index.model_dump_json(indent=2))

    print(f"[SAVED] {out}")


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--ldu_file")
    parser.add_argument("--batch", action="store_true")

    args = parser.parse_args()

    if args.ldu_file:
        process_file(Path(args.ldu_file))

    elif args.batch:
        for f in INPUT_DIR.glob("*.json"):
            process_file(f)


if __name__ == "__main__":
    main()
