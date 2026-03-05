# src/adapters/docling_adapter.py

from typing import List, Optional
from src.models.ldu import LDU
from src.models.extracted_document import ExtractedDocument


class DoclingDocument:
    """
    Lightweight normalized wrapper around Docling output.

    Expected structure:
    pages = [
        {
            "units": [
                {
                    "text": "...",
                    "section_path": [...],
                    "confidence": 0.9
                }
            ]
        }
    ]
    """

    def __init__(self, pages: List[dict]):
        self.pages = pages


class DoclingDocumentAdapter:
    """
    Converts Docling output into the internal LDU schema.
    """

    @staticmethod
    def to_ldus(doc_id: str, docling_doc: DoclingDocument) -> List[LDU]:

        ldus: List[LDU] = []

        for page_idx, page in enumerate(docling_doc.pages):

            for unit in page.get("units", []):

                text = unit.get("text", "").strip()

                if not text:
                    continue

                ldu = LDU.from_text(
                    doc_id=doc_id,
                    text=text,
                    page_number=page_idx + 1,
                    section_path=unit.get("section_path", []),
                    confidence=unit.get("confidence", 0.9),
                )

                ldus.append(ldu)

        return ldus

    @staticmethod
    def from_file_safe(file_path: str) -> Optional[DoclingDocument]:
        """
        Safely attempt to run Docling.

        Returns:
            DoclingDocument if successful
            None if Docling unavailable or fails
        """

        try:
            import docling
        except Exception:
            return None

        try:
            # Docling typical API
            if hasattr(docling, "Document"):

                Doc = getattr(docling, "Document")

                if hasattr(Doc, "from_file"):
                    doc = Doc.from_file(file_path)
                else:
                    doc = Doc(file_path)

            else:
                return None

        except Exception:
            return None

        # Normalize structure
        pages = []

        for page in getattr(doc, "pages", []):

            units = []

            for block in getattr(page, "blocks", []):

                text = getattr(block, "text", "")

                if not text:
                    continue

                units.append(
                    {
                        "text": text,
                        "section_path": [],
                        "confidence": 0.9,
                    }
                )

            pages.append({"units": units})

        return DoclingDocument(pages=pages)
