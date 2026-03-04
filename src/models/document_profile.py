# DocumentProfile model to capture document characteristics for extraction strategy decisions
# src/models/document_profile.py
from pydantic import BaseModel
from typing import Literal, Optional


from .types import OriginType, LayoutComplexity, ExtractionCost

class DocumentProfile(BaseModel):
    doc_id: str

    origin_type: OriginType
    layout_complexity: LayoutComplexity

    language: str
    language_confidence: float

    domain_hint: str

    estimated_extraction_cost: ExtractionCost
