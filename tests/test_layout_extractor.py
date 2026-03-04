# tests/test_layout_extractor.py
from src.strategies.layout_extractor import LayoutExtractor
from src.models.document_profile import DocumentProfile

def test_layout_extractor_runs(sample_pdf_path):
    profile = DocumentProfile(
        doc_id="sample_doc",
        origin_type="native_digital",
        layout_complexity="table_heavy",
        language="en",
        language_confidence=1.0,
        domain_hint="general",
        estimated_extraction_cost="needs_layout_model",
    )

    extractor = LayoutExtractor()
    result = extractor.extract(str(sample_pdf_path), profile)

    assert result.strategy_used == "layout_model"
    assert result.confidence >= 0
    assert result.ldus is not None
