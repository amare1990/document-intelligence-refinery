# src/strategies/base_extractor.py
class BaseExtractor:
    def extract(self, file_path: str) -> dict:
        """Return normalized extracted document structure"""
        raise NotImplementedError
