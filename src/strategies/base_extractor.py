# src/strategies/base_extractor.py
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Protocol

from src.models.document_profile import DocumentProfile
from src.models.extracted_document import ExtractedDocument


class BaseExtractor(ABC):
    """
    Shared contract for all extraction strategies.

    Guarantees:
    - deterministic output schema
    - confidence score for router gating
    - cost estimate surfaced to ledger
    """

    name: str

    @abstractmethod
    def extract(
        self,
        file_path: str,
        profile: DocumentProfile,
    ) -> ExtractedDocument:
        raise NotImplementedError
