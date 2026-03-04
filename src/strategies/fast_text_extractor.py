# src/strategies/fast_text.py
import pdfplumber
from typing import List

from src.strategies.base_extractor import BaseExtractor
from src.models.document_profile import DocumentProfile
from src.models.extracted_document import ExtractedDocument
from src.models.ldu import LDU


class FastTextExtractor(BaseExtractor):
    """
    Strategy A

    Intended for:
    - native_digital
    - low/medium complexity

    Characteristics:
    - very fast
    - cheap
    - no layout reasoning
    """

    name = "fast_text"

    def extract(
        self,
        file_path: str,
        profile: DocumentProfile,
    ) -> ExtractedDocument:

        chunks: List[LDU] = []

        with pdfplumber.open(file_path) as pdf:
            for page_idx, page in enumerate(pdf.pages):
                text = page.extract_text() or ""

                if not text.strip():
                    continue

                chunks.append(
                    LDU.from_text(
                        doc_id=profile.doc_id,
                        text=text,
                        page_number=page_idx + 1
                    )
                )

        confidence = 0.90 if chunks else 0.0

        return ExtractedDocument(
            doc_id=profile.doc_id,
            strategy_used=self.name,
            confidence=confidence,
            ldus=chunks,
            source_path=str(file_path)
        )
