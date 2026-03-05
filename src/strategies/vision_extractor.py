import os
import io
import fitz
from typing import List
from pathlib import Path
from PIL import Image
from dotenv import load_dotenv
from google import genai
from google.genai import types

from src.strategies.base_extractor import BaseExtractor
from src.models.document_profile import DocumentProfile
from src.models.extracted_document import ExtractedDocument
from src.models.ldu import LDU

load_dotenv()

class VisionExtractor(BaseExtractor):
    name = "vision_model"

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in .env")
        self.client = genai.Client(api_key=self.api_key)
        self.model_id = "gemini-2.0-flash"

    def extract(self, file_path: Path, profile: DocumentProfile) -> ExtractedDocument:
        chunks: List[LDU] = []

        with fitz.open(str(file_path)) as doc:
            for page_idx in range(len(doc)):
                page_num = page_idx + 1
                page = doc[page_idx]

                pix = page.get_pixmap(dpi=300)
                img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='PNG')

                try:
                    response = self.client.models.generate_content(
                        model=self.model_id,
                        contents=[
                            types.Part.from_bytes(data=img_byte_arr.getvalue(), mime_type="image/png"),
                            "Extract all text from this page. Return as plain text."
                        ]
                    )
                    if response.text:
                        chunks.append(LDU.from_text(
                            doc_id=profile.doc_id,
                            text=response.text,
                            page_number=page_num,
                            confidence=0.95
                        ))
                except Exception as e:
                    print(f"Error on {file_path.name} page {page_num}: {e}")

        return ExtractedDocument(
            doc_id=profile.doc_id,
            strategy_used=self.name,
            confidence=0.95 if chunks else 0.0,
            ldus=chunks,
            source_path=str(file_path)
        )
