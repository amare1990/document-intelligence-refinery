from pydantic import BaseModel
from typing import Optional


class AuditResult(BaseModel):

    claim: str
    verdict: str  # verified | unsupported | unverifiable
    evidence_ldu: Optional[str] = None
    explanation: Optional[str] = None
