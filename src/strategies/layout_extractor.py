# src/strategies/layout_extractor.py
from typing import List
from src.strategies.base_extractor import BaseExtractor
from src.models.document_profile import DocumentProfile
from src.models.extracted_document import ExtractedDocument
from src.models.ldu import LDU


class LayoutExtractor(BaseExtractor):
    """
    Strategy B: Layout-Aware Extraction
    Intended for multi-column, table-heavy, or mixed-origin documents.
    """

    name = "layout_model"

    def extract(
        self,
        file_path: str,
        profile: DocumentProfile,
    ) -> ExtractedDocument:

        # Skeleton: No real parsing yet
        chunks: List[LDU] = []

        # TODO: integrate MinerU or Docling extraction here

        confidence = 0.85  # placeholder for medium confidence

        return ExtractedDocument(
            doc_id=profile.doc_id,
            strategy_used=self.name,
            confidence=confidence,
            ldus=chunks,
            source_path=file_path
        )
