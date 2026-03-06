# src/agents/chunker.py

"""
Stage 3: Chunking Engine

Transforms extracted document text into Logical Document Units (LDUs)
while preserving document hierarchy and enforcing chunking rules.
"""

import re
import hashlib
from typing import List

from src.models.extracted_document import ExtractedDocument
from src.models.ldu import LDU


class ChunkValidator:
    """
    Enforces the Chunking Constitution rules before emitting LDUs.
    """

    MAX_TOKENS = 400

    def validate(self, text: str) -> str:
        """
        Enforce token limits and structural integrity.
        """
        tokens = text.split()

        if len(tokens) > self.MAX_TOKENS:
            tokens = tokens[: self.MAX_TOKENS]

        return " ".join(tokens)


class SemanticChunker:
    """
    Stage 3 Agent.

    Converts extracted document text into Logical Document Units (LDUs)
    while preserving section hierarchy and enforcing chunking rules.
    """

    # Detect numbered section headers like:
    # 1 Introduction
    # 2.1 Budget Overview
    HEADER_PATTERN = r"^\d+(\.\d+)*\s+.+"

    def __init__(self):
        self.validator = ChunkValidator()

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

            # Detect section headers
            if self._is_header(line):

                # Flush previous chunk
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

        # Flush remaining buffer
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
        """
        Detect section header lines.
        """
        return bool(re.match(self.HEADER_PATTERN, line))

    def _create_ldu(
        self,
        extracted_doc: ExtractedDocument,
        text: str,
        section_path: List[str],
    ) -> LDU:
        """
        Create LDU from buffered text with validation and hashing.
        """

        validated_text = self.validator.validate(text)

        return LDU.from_text(
            doc_id=extracted_doc.doc_id,
            text=validated_text,
            page_number=1,  # placeholder until page-level extraction
            section_path=section_path,
            confidence=extracted_doc.confidence,
        )
