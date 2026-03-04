# src/agents/extractor.py
from src.models.document_profile import DocumentProfile
from src.models.extracted_document import ExtractedDocument
from src.strategies.fast_text_extractor import FastTextExtractor
from src.strategies.layout_extractor import LayoutExtractor
from src.strategies.vision_extractor import VisionExtractor


class ExtractionRouter:
    """
    Stage 2 Orchestrator

    Selects strategy based on:
    - origin_type
    - layout_complexity
    - estimated_extraction_cost

    Escalates if confidence < threshold.
    """

    CONFIDENCE_THRESHOLD = 0.80

    def __init__(self) -> None:
        self.strategies = {
            "fast_text": FastTextExtractor(),
            "layout_model": LayoutExtractor(),
            "vision_model": VisionExtractor(),
        }

    def route(
        self,
        file_path: str,
        profile: DocumentProfile,
    ) -> ExtractedDocument:

        # Phase 2 routing logic
        if profile.estimated_extraction_cost == "fast_text_sufficient":
            extractor = self.strategies["fast_text"]
        elif profile.estimated_extraction_cost == "needs_layout_model":
            extractor = self.strategies["layout_model"]
        else:  # "needs_vision_model"
            extractor = self.strategies["vision_model"]

        result = extractor.extract(file_path, profile)

        # Escalation guard
        if result.confidence < self.CONFIDENCE_THRESHOLD:
            # escalate to next higher-cost strategy
            if extractor.name == "fast_text":
                result = self.strategies["layout_model"].extract(file_path, profile)
            elif extractor.name == "layout_model":
                result = self.strategies["vision_model"].extract(file_path, profile)


        return result
