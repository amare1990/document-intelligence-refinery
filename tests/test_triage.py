# tests/test_triage.py
from src.agents.triage import TriageAgent


def test_origin_rules():
    agent = TriageAgent()

    stats = {"char_density": 0.0, "image_ratio": 0.9, "line_count": 0}
    assert agent.classify_origin(stats) == "scanned_image"


def test_layout_rules():
    agent = TriageAgent()

    stats = {"char_density": 1.0, "image_ratio": 0.0, "line_count": 20}
    assert agent.classify_layout(stats) == "table_heavy"
