# src/agents/semantic_chunker.py

import re
from typing import List

from src.models.extracted_document import ExtractedDocument
from src.models.ldu import LDU


class SemanticChunker:
    """
    Stage 3 Agent.

    Converts extracted document text into Logical Document Units (LDUs).
    """

    def chunk(self, extracted_doc: ExtractedDocument) -> ExtractedDocument:
        if not extracted_doc.raw_text:
            return extracted_doc

        paragraphs = self._split_into_blocks(extracted_doc.raw_text)

        ldus: List[LDU] = []

        for block in paragraphs:
            ldu = LDU.from_text(
                doc_id=extracted_doc.doc_id,
                text=block,
                page_number=1,
                confidence=extracted_doc.confidence,
                section_path=[],
            )

            ldus.append(ldu)

        extracted_doc.ldus = ldus
        return extracted_doc

    def _split_into_blocks(self, text: str) -> List[str]:
        """
        Split document into semantic blocks.
        """
        blocks = re.split(r"\n\s*\n", text)
        return [b.strip() for b in blocks if b.strip()]
