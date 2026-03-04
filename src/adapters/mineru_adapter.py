# src/adapters/mineru_adapter.py
from typing import List
from src.models.ldu import LDU

# Placeholder for MinerUDocument
class MinerUDocument:
    """Raw output from MinerU model."""
    def __init__(self, content: list[dict]):
        self.content = content


class MinerUAdapter:
    """
    Converts MinerU extraction output into LDU list.
    """

    @staticmethod
    def to_ldus(doc_id: str, mineru_doc: MinerUDocument) -> List[LDU]:
        ldus: List[LDU] = []

        for page_idx, page in enumerate(mineru_doc.content):
            for block in page.get("blocks", []):
                ldus.append(
                    LDU.from_text(
                        doc_id=doc_id,
                        text=block.get("text", ""),
                        page_number=page_idx + 1,
                        section_path=block.get("section_path", []),
                        confidence=block.get("confidence", 0.85),
                    )
                )

        return ldus
