# src/agents/extractor.py
from src.models.document_profile import DocumentProfile
from src.models.extracted_document import ExtractedDocument
from src.strategies.fast_text_extractor import FastTextExtractor


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
        self.fast = FastTextExtractor()

    def route(
        self,
        file_path: str,
        profile: DocumentProfile,
    ) -> ExtractedDocument:

        result = self.fast.extract(file_path, profile)

        if result.confidence >= self.CONFIDENCE_THRESHOLD:
            return result

        # future escalation:
        # -> LayoutExtractor
        # -> VisionExtractor

        return result
