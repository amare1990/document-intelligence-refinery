from typing import Literal
from src.models.document_profile import DocumentProfile

OriginType = Literal["native_digital", "scanned_image", "mixed", "form_fillable"]
LayoutType = Literal["single_column", "multi_column", "table_heavy", "figure_heavy", "mixed"]

class TriageAgent:
    def classify_origin(self, file_path: str) -> OriginType:
        """Detect native vs scanned document."""
        raise NotImplementedError

    def classify_layout(self, file_path: str) -> LayoutType:
        """Determine layout complexity."""
        raise NotImplementedError

    def classify_domain(self, file_path: str) -> str:
        """Assign domain hint."""
        raise NotImplementedError

    def generate_profile(self, file_path: str) -> DocumentProfile:
        """Produce DocumentProfile for downstream routing."""
        raise NotImplementedError
