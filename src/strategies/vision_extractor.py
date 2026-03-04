# src/strategies/vision_extractor.py
from typing import List
from src.strategies.base_extractor import BaseExtractor
from src.models.document_profile import DocumentProfile
from src.models.extracted_document import ExtractedDocument
from src.models.ldu import LDU


class VisionExtractor(BaseExtractor):
    """
    Strategy C: Vision-Augmented Extraction
    Intended for scanned or low-confidence pages.
    """

    name = "vision_model"

    def extract(
        self,
        file_path: str,
        profile: DocumentProfile,
    ) -> ExtractedDocument:

        chunks: List[LDU] = []

        # TODO: integrate VLM OCR / multimodal extraction here

        confidence = 0.95  # placeholder for high-confidence VLM output

        return ExtractedDocument(
            doc_id=profile.doc_id,
            strategy_used=self.name,
            confidence=confidence,
            ldus=chunks,
            source_path=file_path
        )
