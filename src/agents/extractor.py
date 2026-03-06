# src/agents/extractor.py

import time
from src.utils.ledger import log_entry

from pathlib import Path

from src.models.document_profile import DocumentProfile
from src.models.extracted_document import ExtractedDocument

from src.strategies.fast_text_extractor import FastTextExtractor
from src.strategies.layout_extractor import LayoutExtractor
from src.strategies.vision_extractor import VisionExtractor


class ExtractionRouter:
    """
    Stage 2 Orchestrator

    Strategy selection:
        estimated_extraction_cost → base strategy

    Escalation:
        fast_text → layout_model → vision_model
        until confidence threshold satisfied.
    """

    # Define the storage location
    STORAGE_DIR = Path(".refinery/extractions")

    CONFIDENCE_THRESHOLD = 0.80

    # cost class → first strategy
    COST_TO_STRATEGY = {
        "fast_text_sufficient": "fast_text",
        "needs_layout_model": "layout_model",
        "needs_vision_model": "vision_model",
    }

    # ordered escalation chain (cheap → expensive)
    ESCALATION_ORDER = [
        "fast_text",
        "layout_model",
        "vision_model",
    ]

    def __init__(self) -> None:
        self.strategies = {
            "fast_text": FastTextExtractor(),
            "layout_model": LayoutExtractor(),
            "vision_model": VisionExtractor(),
        }

        # 3️⃣ Ensure the storage directory exists on initialization
        self.STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    def _persist_result(self, result: ExtractedDocument, original_path: str):
        """Internal helper to save the JSON to disk."""
        file_stem = Path(original_path).stem
        output_path = self.STORAGE_DIR / f"{file_stem}.json"

        # Debug print to see where it's trying to save
        print(f"[DEBUG] Attempting to save to: {output_path.absolute()}")

        with open(output_path, "w", encoding="utf-8") as f:
            # Assuming ExtractedDocument is a Pydantic model
            f.write(result.model_dump_json(indent=2))

        return output_path

    def route(
        self,
        file_path: str,
        profile: DocumentProfile,
    ) -> ExtractedDocument:

        start = time.time()

        # ----------------------------
        # 1. initial strategy selection
        # ----------------------------
        first_key = self.COST_TO_STRATEGY[profile.estimated_extraction_cost]
        start_index = self.ESCALATION_ORDER.index(first_key)

        result: ExtractedDocument

        # ----------------------------
        # 2. attempt with escalation
        # ----------------------------
        for key in self.ESCALATION_ORDER[start_index:]:
            extractor = self.strategies[key]
            candidate = extractor.extract(file_path, profile)

            result = candidate

            if candidate.confidence >= self.CONFIDENCE_THRESHOLD:
                break

        assert result is not None


        # Save to .refinery/extractions before returning
        saved_path = self._persist_result(result, file_path)

        # ----------------------------
        # 3. ledger logging
        # ----------------------------
        elapsed_ms = int((time.time() - start) * 1000)

        log_entry({
            "doc_id": profile.doc_id,
            "source_path": file_path,
            "strategy_used": result.strategy_used,
            "confidence_score": result.confidence,
            "estimated_extraction_cost": profile.estimated_extraction_cost,
            "processing_time_ms": elapsed_ms,
        })

        return result
