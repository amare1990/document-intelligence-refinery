# src/agents/chunker.py

"""
Stage 3: Chunking Engine

Transforms extracted document text into Logical Document Units (LDUs)
while preserving document hierarchy and enforcing chunking rules.
"""

from pydoc import text
import re
import hashlib
from typing import List

from src.models.extracted_document import ExtractedDocument
from src.models.ldu import LDU


class ChunkValidator:

    MAX_TOKENS = 400

    def validate(self, text: str, chunk_type: str, section_path: list[str]) -> str:

        if not text.strip():
            raise ValueError("Empty chunk detected")

        tokens = text.split()

        if len(tokens) > self.MAX_TOKENS:
            tokens = tokens[: self.MAX_TOKENS]

        text = " ".join(tokens)

        if chunk_type == "table":
            self._validate_table(text)

        if chunk_type == "list":
            self._validate_list(text)

        if chunk_type != "header" and not section_path:
            raise ValueError("Missing section metadata")

        return text


    def _validate_table(self, text: str):

        rows = text.split("\n")

        if len(rows) < 2:
            raise ValueError("Table missing rows")

        header_cols = len(rows[0].split("|"))

        for row in rows[1:]:
            if len(row.split("|")) != header_cols:
                raise ValueError("Column mismatch in table")


    def _validate_list(self, text: str):

        items = text.split("\n")

        for item in items:
            if not re.match(r"^\d+\.", item):
                raise ValueError("Invalid list structure")


class SemanticChunker:
    """
    Stage 3 Agent.

    Converts extracted document text into Logical Document Units (LDUs)
    while preserving section hierarchy and enforcing chunking rules.
    """

    HEADER_PATTERN = r"^\d+(\.\d+)*\s+.+"
    LIST_PATTERN = r"^\d+\.\s+.+"
    FIGURE_PATTERN = r"^(Figure|Fig\.)\s*\d+"
    CROSS_REF_PATTERN = r"(Table|Figure)\s+\d+"

    def __init__(self):
        self.validator = ChunkValidator()

    def chunk(self, extracted_doc: ExtractedDocument) -> ExtractedDocument:

        if not extracted_doc.raw_text:
            return extracted_doc

        lines = extracted_doc.raw_text.split("\n")

        ldus: List[LDU] = []

        buffer: List[str] = []
        current_section: List[str] = []
        current_type = "paragraph"

        for line in lines:

            line = line.strip()

            if not line:
                continue

            # HEADER
            if self._is_header(line):

                if buffer:
                    ldus.append(
                        self._create_ldu(
                            extracted_doc,
                            " ".join(buffer),
                            current_section,
                            current_type,
                        )
                    )
                    buffer = []

                current_section = [line]
                current_type = "header"
                continue

            # FIGURE
            if self._is_figure(line):

                if buffer:
                    ldus.append(
                        self._create_ldu(
                            extracted_doc,
                            " ".join(buffer),
                            current_section,
                            current_type,
                        )
                    )
                    buffer = []

                ldus.append(
                    self._create_ldu(
                        extracted_doc,
                        line,
                        current_section,
                        "figure",
                    )
                )

                continue

            # LIST ITEM
            if self._is_list_item(line):
                current_type = "list"
                buffer.append(line)
                continue

            # TABLE ROW
            if self._is_table_row(line):
                current_type = "table"
                buffer.append(line)
                continue

            # DEFAULT PARAGRAPH
            current_type = "paragraph"
            buffer.append(line)

        if buffer:
            ldus.append(
                self._create_ldu(
                    extracted_doc,
                    " ".join(buffer),
                    current_section,
                    current_type,
                )
            )

        extracted_doc.ldus = ldus
        return extracted_doc

    def _is_header(self, line: str) -> bool:
        return bool(re.match(self.HEADER_PATTERN, line))

    def _is_list_item(self, line: str) -> bool:
        return bool(re.match(self.LIST_PATTERN, line))

    def _is_table_row(self, line: str) -> bool:
        return "|" in line

    def _is_figure(self, line: str) -> bool:
        return bool(re.match(self.FIGURE_PATTERN, line))

    def _extract_figure_metadata(self, text: str):

        caption = text

        return {
            "caption": caption
        }

    def _extract_references(self, text: str) -> List[str]:
        return re.findall(self.CROSS_REF_PATTERN, text)


    def _create_ldu(
        self,
        extracted_doc: ExtractedDocument,
        text: str,
        section_path: List[str],
        chunk_type: str,
    ) -> LDU:

        validated_text = self.validator.validate(text, chunk_type, section_path)

        ldu = LDU.from_text(
            doc_id=extracted_doc.doc_id,
            text=validated_text,
            page_number=1,
            section_path=section_path,
            confidence=extracted_doc.confidence,
        )

        ldu.chunk_type = chunk_type

        # Extract cross references
        ldu.references = self._extract_references(validated_text)

        # Attach metadata depending on type
        if chunk_type == "figure":
            ldu.metadata = self._extract_figure_metadata(validated_text)

        if chunk_type == "table":
            rows = validated_text.split("\n")
            ldu.metadata["rows"] = len(rows)
            ldu.metadata["columns"] = len(rows[0].split("|"))

        if chunk_type == "list":
            ldu.metadata["items"] = len(validated_text.split("\n"))

        return ldu
