# src/pipelines/run_vision_extraction.py
import argparse
import json
from pathlib import Path
from typing import List

from src.strategies.vision_extractor import VisionExtractor
from src.models.document_profile import DocumentProfile
from src.models.extracted_document import ExtractedDocument

def save_extraction_result(extraction: ExtractedDocument, output_dir: Path):
    """Saves the ExtractedDocument model to a JSON file using Pydantic V2 methods."""
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{extraction.doc_id}_extracted.json"
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(extraction.model_dump(), f, indent=4, ensure_ascii=False)
        print(f"[SAVED] {output_file.name}")
    except Exception as e:
        print(f"[ERROR] Failed to save {extraction.doc_id}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Vision-only extraction pipeline")
    parser.add_argument("--batch", action="store_true", help="Process all profiles in .refinery/profiles")
    parser.add_argument("--profile", type=str, help="Process a single DocumentProfile JSON")
    parser.add_argument("--out-dir", type=str, default=".refinery/extractions", help="Output folder")
    parser.add_argument("--data-dir", type=str, default="data", help="Folder containing PDF source files")

    args = parser.parse_args()
    out_path = Path(args.out_dir)
    data_root = Path(args.data_dir)
    extractor = VisionExtractor()

    # --- Single profile mode ---
    if args.profile:
        profile_file = Path(args.profile)
        if not profile_file.exists():
            print(f"[!] Profile not found: {profile_file}")
            return

        profile = DocumentProfile.model_validate(json.loads(profile_file.read_text()))
        pdf_path = data_root / f"{profile.doc_id}.pdf"
        if not pdf_path.exists():
            print(f"[!] PDF file missing for {profile.doc_id}: {pdf_path}")
            return

        print(f"[*] Extracting Vision from {profile.doc_id}...")
        result = extractor.extract(pdf_path, profile)
        save_extraction_result(result, out_path)

    # --- Batch mode ---
    elif args.batch:
        profile_dir = Path(".refinery/profiles")
        if not profile_dir.exists():
            print(f"[!] Profile directory missing: {profile_dir}")
            return

        for profile_file in profile_dir.glob("*.json"):
            profile = DocumentProfile.model_validate(json.loads(profile_file.read_text()))
            pdf_path = data_root / f"{profile.doc_id}.pdf"
            if not pdf_path.exists():
                print(f"[!] PDF file missing for {profile.doc_id}")
                continue

            print(f"[*] Extracting Vision from {profile.doc_id}...")
            result = extractor.extract(pdf_path, profile)
            save_extraction_result(result, out_path)

    else:
        print("[!] Specify --profile <file> or --batch to run the extraction.")
        parser.print_help()

if __name__ == "__main__":
    main()
