import re
from typing import List

from src.models.extracted_document import ExtractedDocument
from src.models.ldu import LDU


class SemanticChunker:
    """
    Stage 3 Agent.

    Converts extracted document text into Logical Document Units (LDUs)
    while preserving document hierarchy when possible.
    """

    # Detects numbered section headers like:
    # 1 Introduction
    # 2.1 Budget Overview
    HEADER_PATTERN = r"^\d+(\.\d+)*\s+.+"

    def chunk(self, extracted_doc: ExtractedDocument) -> ExtractedDocument:
        """
        Transform raw extracted text into structured LDUs.
        """

        if not extracted_doc.raw_text:
            return extracted_doc

        lines = extracted_doc.raw_text.split("\n")

        ldus: List[LDU] = []

        buffer: List[str] = []
        current_section: List[str] = []

        for line in lines:

            line = line.strip()

            if not line:
                continue

            # Detect section header
            if self._is_header(line):

                # flush previous block
                if buffer:
                    ldus.append(
                        self._create_ldu(
                            extracted_doc,
                            " ".join(buffer),
                            current_section
                        )
                    )
                    buffer = []

                current_section = [line]
                continue

            buffer.append(line)

        # flush final block
        if buffer:
            ldus.append(
                self._create_ldu(
                    extracted_doc,
                    " ".join(buffer),
                    current_section
                )
            )

        extracted_doc.ldus = ldus
        return extracted_doc

    def _is_header(self, line: str) -> bool:
        """Detect section header lines."""
        return bool(re.match(self.HEADER_PATTERN, line))

    def _create_ldu(
        self,
        extracted_doc: ExtractedDocument,
        text: str,
        section_path: List[str],
    ) -> LDU:
        """
        Create LDU from buffered text.
        """

        return LDU.from_text(
            doc_id=extracted_doc.doc_id,
            text=text,
            page_number=1,  # placeholder until page-level extraction
            section_path=section_path,
            confidence=extracted_doc.confidence,
        )
