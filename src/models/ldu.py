# src/models/ldu.py
from pydantic import BaseModel, Field
from typing import List, Optional

import uuid
from hashlib import sha256


class BoundingBox(BaseModel):
    """Spatial coordinates on page."""
    x0: float
    y0: float
    x1: float
    y1: float


class LDU(BaseModel):
    """
    Logical Document Unit.

    Represents the smallest semantically meaningful chunk:
    paragraph, table cell group, figure caption, etc.
    """

    ldu_id: str
    doc_id: str

    page_number: int
    bbox: Optional[BoundingBox] = None

    text: str
    content_hash: str

    section_path: List[str] = Field(
        default_factory=list,
        description="Hierarchical location e.g. ['3', '3.2', 'Financial Results']"
    )

    token_count: int
    confidence: float = Field(ge=0.0, le=1.0)

    chunk_type: str = Field(
        default="paragraph",
        description="paragraph | table | figure | list | header"
    )

    metadata: dict = Field(default_factory=dict)
    references: list[str] = Field(default_factory=list)

    @classmethod
    def from_text(
        cls,
        doc_id: str,
        text: str,
        page_number: int,
        section_path: list[str] | None = None,
        confidence: float = 1.0,
        bbox: BoundingBox | None = None,
    ) -> "LDU":
        """
        Factory helper to create LDU from raw text.
        Generates ldu_id and content_hash automatically.
        """
        if section_path is None:
            section_path = []

        content_hash = sha256(text.encode("utf-8")).hexdigest()
        token_count = len(text.split())

        return cls(
            ldu_id=str(uuid.uuid4()),
            doc_id=doc_id,
            page_number=page_number,
            bbox=bbox,
            text=text,
            content_hash=content_hash,
            section_path=section_path,
            token_count=token_count,
            confidence=confidence,
        )
