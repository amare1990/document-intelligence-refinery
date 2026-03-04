# src/models/ldu.py
from pydantic import BaseModel, Field
from typing import List, Optional


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
