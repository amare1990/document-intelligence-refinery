"""
Audit Agent

Verifies whether retrieved document evidence supports a user query.

This agent prevents hallucinations by validating that claims are
grounded in retrieved LDUs.
"""

from typing import List

from src.models.audit_result import AuditResult


class AuditAgent:
    """
    Claim verification agent.

    Validates that retrieved LDUs actually support the user query.
    """

    def verify_claim(
        self,
        query: str,
        evidence_texts: List[str],
    ) -> AuditResult:

        if not evidence_texts:
            return AuditResult(
                verified=False,
                confidence=0.0,
                status="unverifiable",
                supporting_evidence=[],
            )

        score = 0
        supporting = []

        query_terms = set(query.lower().split())

        for text in evidence_texts:

            tokens = set(text.lower().split())

            overlap = query_terms.intersection(tokens)

            if overlap:
                score += len(overlap)
                supporting.append(text)

        confidence = min(score / (len(query_terms) + 1), 1.0)

        verified = confidence > 0.2

        status = "verified" if verified else "unverifiable"

        return AuditResult(
            verified=verified,
            confidence=confidence,
            status=status,
            supporting_evidence=supporting,
        )
