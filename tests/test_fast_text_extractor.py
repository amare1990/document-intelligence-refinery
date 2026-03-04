from src.agents.extractor import ExtractionRouter
from src.models.document_profile import DocumentProfile


def test_fast_text_strategy_runs(sample_pdf_path):
    profile = DocumentProfile(
        doc_id="sample_native_doc",
        origin_type="native_digital",
        layout_complexity="single_column",
        language="en",
        language_confidence=1.0,
        domain_hint="general",
        estimated_extraction_cost="fast_text_sufficient",
    )

    router = ExtractionRouter()

    # result = router.route(sample_pdf_path, profile)
    result = router.route(str(sample_pdf_path), profile)

    assert result.strategy_used == "fast_text"
    assert result.confidence >= 0
