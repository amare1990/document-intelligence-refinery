from pydantic import BaseModel
from typing import List


class AuditResult(BaseModel):

    verified: bool
    confidence: float
    status: str  # "verified" | "unverifiable"
    supporting_evidence: List[str]
