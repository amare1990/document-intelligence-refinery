from src.models.document_profile import DocumentProfile
from src.strategies.fast_text_extractor import FastTextExtractor
from src.strategies.layout_extractor import LayoutExtractor
from src.strategies.vision_extractor import VisionExtractor

class ExtractionRouter:
    def __init__(self):
        self.strategy_a = FastTextExtractor()
        self.strategy_b = LayoutExtractor()
        self.strategy_c = VisionExtractor()

    def route(self, profile: DocumentProfile, file_path: str):
        # Route to appropriate strategy based on profile and confidence
        pass
