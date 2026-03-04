# src/adapters/docling_adapter.py
from typing import List
from src.models.ldu import LDU
from src.models.extracted_document import ExtractedDocument

# Placeholder for the DoclingDocument type
class DoclingDocument:
    """Represents raw output from Docling model (mocked for now)."""
    def __init__(self, pages: list[dict]):
        self.pages = pages


class DoclingDocumentAdapter:
    """
    Normalizes DoclingDocument output into internal LDU schema.
    """

    @staticmethod
    def to_ldus(doc_id: str, docling_doc: DoclingDocument) -> List[LDU]:
        ldus: List[LDU] = []

        for page_idx, page in enumerate(docling_doc.pages):
            for unit in page.get("units", []):  # e.g., paragraphs, table cells
                ldus.append(
                    LDU.from_text(
                        doc_id=doc_id,
                        text=unit.get("text", ""),
                        page_number=page_idx + 1,
                        section_path=unit.get("section_path", []),
                        confidence=unit.get("confidence", 0.9),
                    )
                )

        return ldus
