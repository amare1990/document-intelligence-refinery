# tests/conftest.py
import pytest
from pathlib import Path
from reportlab.pdfgen import canvas

@pytest.fixture
def sample_pdf_path(tmp_path):
    """
    Creates a minimal PDF file for testing.
    tmp_path is a built-in pytest fixture providing a temp directory.
    """
    pdf_path = tmp_path / "sample.pdf"

    c = canvas.Canvas(str(pdf_path))
    c.drawString(100, 750, "Hello, this is a test PDF.")
    c.save()

    return pdf_path
