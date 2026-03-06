# src/models/provenance_chain.py

from pydantic import BaseModel, Field
from typing import List, Optional

from src.models.audit_result import AuditResult


class ProvenanceStep(BaseModel):
    """
    A single trace step linking answer → chunk → document location.
    """

    doc_id: str
    ldu_id: str

    page_number: int
    bbox: Optional[List[float]] = None  # [x0, y0, x1, y1]

    content_hash: str
    confidence: float

    section_path: List[str] = []


class ProvenanceChain(BaseModel):
    """
    Ordered provenance from answer back to original source.
    """

    query: str

    steps: List[ProvenanceStep]

    overall_confidence: float = Field(ge=0.0, le=1.0)

    audit: Optional[AuditResult] = None
