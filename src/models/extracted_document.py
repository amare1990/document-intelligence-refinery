# src/models/extracted_document.py
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from .ldu import LDU


class ExtractedDocument(BaseModel):
    """
    Canonical normalized representation of a parsed document.

    This is the single object produced by all extractors
    (FastText, Layout, Vision) before chunking.
    """

    doc_id: str = Field(..., description="Stable document identifier")
    source_path: str = Field(..., description="Original file location")

    strategy_used: str = Field(..., description="A | B | C extraction strategy")
    confidence: float = Field(..., ge=0.0, le=1.0)

    raw_text: Optional[str] = None
    metadata: Dict[str, str] = {}

    # After chunking this gets populated
    ldus: List[LDU] = Field(default_factory=list)
