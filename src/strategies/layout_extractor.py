# src/strategies/layout_extractor.py

from typing import List
import pdfplumber

from src.strategies.base_extractor import BaseExtractor
from src.models.document_profile import DocumentProfile
from src.models.extracted_document import ExtractedDocument
from src.models.ldu import LDU, BoundingBox
from src.adapters.docling_adapter import DoclingDocumentAdapter


class LayoutExtractor(BaseExtractor):
    """
    Strategy B — Layout Aware Extraction.

    Medium-cost extractor used for:
    - multi-column documents
    - table-heavy PDFs
    - structured reports

    Pipeline:
    1) Try Docling (advanced layout model)
    2) Fallback to pdfplumber
    """

    name = "layout_model"

    def extract(
        self,
        file_path: str,
        profile: DocumentProfile,
    ) -> ExtractedDocument:

        chunks: List[LDU] = []

        # -------------------------
        # Strategy 1: Docling
        # -------------------------

        docling_doc = DoclingDocumentAdapter.from_file_safe(file_path)

        if docling_doc is not None:

            chunks = DoclingDocumentAdapter.to_ldus(
                profile.doc_id,
                docling_doc
            )

            confidence = 0.9 if chunks else 0.0

            return ExtractedDocument(
                doc_id=profile.doc_id,
                source_path=str(file_path),
                strategy_used=self.name,
                confidence=confidence,
                ldus=chunks,
            )

        # -------------------------
        # Strategy 2: pdfplumber fallback
        # -------------------------

        with pdfplumber.open(file_path) as pdf:

            for page_idx, page in enumerate(pdf.pages):

                page_number = page_idx + 1

                # -------------------------
                # Tables
                # -------------------------

                try:
                    tables = page.find_tables()
                except Exception:
                    tables = []

                for table in tables:

                    rows = table.extract()

                    table_text = "\n".join(
                        ["\t".join(cell or "" for cell in row) for row in rows]
                    )

                    bbox = BoundingBox(
                        x0=table.bbox[0],
                        y0=table.bbox[1],
                        x1=table.bbox[2],
                        y1=table.bbox[3],
                    )

                    chunks.append(
                        LDU.from_text(
                            doc_id=profile.doc_id,
                            text=f"[TABLE]\n{table_text}",
                            page_number=page_number,
                            bbox=bbox,
                            confidence=0.9,
                        )
                    )

                # -------------------------
                # Text blocks
                # -------------------------

                words = page.extract_words()

                if not words:
                    continue

                lines = {}

                for w in words:

                    y = round(w.get("top", 0), 1)

                    lines.setdefault(y, []).append(w)

                for _, wordlist in sorted(lines.items()):

                    text = " ".join(w.get("text", "") for w in wordlist).strip()

                    if not text:
                        continue

                    x0 = min(float(w["x0"]) for w in wordlist)
                    x1 = max(float(w["x1"]) for w in wordlist)
                    y0 = min(float(w["top"]) for w in wordlist)
                    y1 = max(float(w["bottom"]) for w in wordlist)

                    bbox = BoundingBox(
                        x0=x0,
                        y0=y0,
                        x1=x1,
                        y1=y1,
                    )

                    chunks.append(
                        LDU.from_text(
                            doc_id=profile.doc_id,
                            text=text,
                            page_number=page_number,
                            bbox=bbox,
                            confidence=0.85,
                        )
                    )

        confidence = 0.85 if chunks else 0.0

        return ExtractedDocument(
            doc_id=profile.doc_id,
            source_path=str(file_path),
            strategy_used=self.name,
            confidence=confidence,
            ldus=chunks,
        )
