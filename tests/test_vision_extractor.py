# tests/test_vision_extractor.py
from src.strategies.vision_extractor import VisionExtractor
from src.agents.triage import TriageAgent

def test_vision_extractor_runs(sample_pdf_path):
    # Use triage to generate realistic profile
    triage = TriageAgent()
    profile = triage.generate_profile(str(sample_pdf_path))

    extractor = VisionExtractor()
    result = extractor.extract(str(sample_pdf_path), profile)

    assert result.strategy_used == "vision_model"
    assert result.confidence >= 0
    assert result.ldus is not None
