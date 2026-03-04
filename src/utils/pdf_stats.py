import pdfplumber


class PDFStats:
    """
    Low-level measurable signals for triage decisions.
    Pure functions → easy to test.
    """

    @staticmethod
    def analyze(path: str) -> dict:
        with pdfplumber.open(path) as pdf:
            pages = pdf.pages

            total_chars = 0
            total_area = 0
            image_area = 0
            line_count = 0

            for p in pages:
                width, height = p.width, p.height
                total_area += width * height

                chars = p.chars or []
                total_chars += len(chars)

                images = p.images or []
                for img in images:
                    image_area += img["width"] * img["height"]

                lines = p.lines or []
                line_count += len(lines)

        return {
            "pages": len(pages),
            "total_chars": total_chars,
            "char_density": total_chars / max(total_area, 1),
            "image_ratio": image_area / max(total_area, 1),
            "line_count": line_count,
        }
