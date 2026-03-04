from langdetect import detect, DetectorFactory

DetectorFactory.seed = 0  # deterministic


def detect_language(text: str):
    """
    Lightweight language detection.
    Returns (language_code, confidence proxy).
    """
    if not text or len(text) < 50:
        return "unknown", 0.0

    try:
        lang = detect(text)
        return lang, 0.9  # langdetect doesn't give confidence; use heuristic
    except Exception:
        return "unknown", 0.0
