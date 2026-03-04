from pathlib import Path
import json
import yaml

from src.models.document_profile import DocumentProfile

from src.utils.pdf_stats import PDFStats
from src.utils.language import detect_language

from src.models.types import OriginType, LayoutComplexity, ExtractionCost

import pdfplumber


class TriageAgent:
    """
    Stage 1 of the Refinery.

    Responsibilities:
    - detect origin_type
    - detect layout_complexity
    - assign domain_hint
    - estimate extraction_cost tier
    - persist DocumentProfile JSON
    """

    def __init__(self, rules_path="rubric/extraction_rules.yaml"):
        with open(rules_path) as f:
            self.rules = yaml.safe_load(f)["triage"]

    # -----------------------------
    # Origin detection
    # -----------------------------
    def classify_origin(self, stats: dict) -> OriginType:
        if stats["char_density"] < self.rules["scanned_char_density_threshold"]:
            return "scanned_image"

        if stats["image_ratio"] > self.rules["image_area_ratio_threshold"]:
            return "mixed"

        return "native_digital"

    # -----------------------------
    # Layout complexity
    # -----------------------------
    def classify_layout(self, stats: dict) -> LayoutComplexity:
        if stats["line_count"] > self.rules["table_line_threshold"]:
            return "table_heavy"

        return "single_column"

    # -----------------------------
    # Domain hint (simple heuristic)
    # -----------------------------
    def classify_domain(self, text: str) -> str:
        text = text.lower()

        if any(k in text for k in ["revenue", "balance sheet", "income statement"]):
            return "financial"

        if any(k in text for k in ["section", "clause", "pursuant"]):
            return "legal"

        return "general"

    # -----------------------------
    # Extraction cost tier
    # -----------------------------
    def estimate_cost(self, origin: OriginType, layout: LayoutComplexity) -> ExtractionCost:
        if origin == "scanned_image":
            return "needs_vision_model"

        if layout == "table_heavy":
            return "needs_layout_model"

        return "fast_text_sufficient"

    # -----------------------------
    # Main entry
    # -----------------------------
    def generate_profile(self, file_path: str) -> DocumentProfile:
        stats = PDFStats.analyze(file_path)

        origin = self.classify_origin(stats)
        layout = self.classify_layout(stats)

        sample_text = self._sample_text(file_path)

        language, language_confidence = detect_language(sample_text)
        domain = self.classify_domain(sample_text)

        profile = DocumentProfile(
            doc_id=Path(file_path).stem,
            origin_type=origin,
            layout_complexity=layout,
            language=language,
            language_confidence=language_confidence,
            domain_hint=domain,
            estimated_extraction_cost=self.estimate_cost(origin, layout),
        )

        self._persist(profile)
        return profile

    def _sample_text(self, path: str, max_pages: int = 3) -> str:
        """Extract small sample for language + domain hint detection."""
        text = []

        with pdfplumber.open(path) as pdf:
            for page in pdf.pages[:max_pages]:
                text.append(page.extract_text() or "")

        return "\n".join(text)



    def _persist(self, profile: DocumentProfile):
        out_dir = Path(".refinery/profiles")
        out_dir.mkdir(parents=True, exist_ok=True)

        path = out_dir / f"{profile.doc_id}.json"
        path.write_text(profile.model_dump_json(indent=2))
