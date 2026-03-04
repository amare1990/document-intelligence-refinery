from typing import Literal

OriginType = Literal[
    "native_digital",
    "scanned_image",
    "mixed",
    "form_fillable",
]

LayoutComplexity = Literal[
    "single_column",
    "multi_column",
    "table_heavy",
    "figure_heavy",
    "mixed",
]

ExtractionCost = Literal[
    "fast_text_sufficient",
    "needs_layout_model",
    "needs_vision_model",
]
