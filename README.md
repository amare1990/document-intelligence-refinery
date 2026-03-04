

---

# Document Intelligence Refinery


The **Document Intelligence Refinery** is a modular, agent-driven pipeline for analyzing, parsing, and structuring heterogeneous documents (PDFs, scans, images). It features a **triage stage** to classify document properties and a **multi-strategy extraction engine** that adapts based on origin, layout, and estimated extraction cost. Extraction strategies include:

* **Strategy A – FastTextExtractor**: Fast, low-cost text extraction for native digital documents.
* **Strategy B – LayoutExtractor (Docling/ MinerU)**: Layout-aware extraction for table-heavy or multi-column documents.
* **Strategy C – VisionExtractor**: Vision-augmented extraction for scanned/low-confidence documents.

A **confidence-gated router** escalates extraction automatically if the initial strategy yields low confidence. All extraction events are logged in `.refinery/extraction_ledger.jsonl` for traceability and auditing.

---
## Author:

Name: Amare kassa
email: amaremek@gmail.com

---

## Requirements

* Python 3.12+
* `uv` package manager
* Core dependencies: `pydantic`, `pytest`, `pdfplumber`
* Layout strategy: `docling`, `torch`, `transformers`
* Optional: `minerU` (alternative to Docling)

---

## Setup

### 1. Create environment

```bash
uv venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
# Core
uv install
uv sync

# Layout strategy (Docling)
uv add git+https://github.com/DS4SD/docling.git
uv add torch transformers
```

---

## Project Structure

```text
src/
├── agents/
│   ├── triage.py              # Stage 1: TriageAgent
│   └── extractor.py           # Stage 2: ExtractionRouter
├── models/
│   ├── document_profile.py
│   ├── extracted_document.py
│   ├── ldu.py
│   ├── page_index.py
│   └── provenance_chain.py
├── strategies/
│   ├── fast_text_extractor.py
│   ├── layout_extractor.py
│   └── vision_extractor.py
├── pipelines/
│   ├── run_triage_batch.py
│   └── run_extraction_batch.py
└── utils/
    ├── pdf_stats.py
    └── language.py
    └── ledger.py
    └── pdf_stats.py

.refinery/
├── profiles/                  # JSON output from TriageAgent
└── extraction_ledger.jsonl    # Logs extraction attempts
rubric/
└── extraction_rules.yaml      # Chunking thresholds and rules
data/
└── *.pdf                      # Source documents for testing
```

---

## Usage
### Assume
```
sample-pdf
```

### 1. Run Triage (Stage 1)

**Single PDF:**


```bash
uv run python -m src.pipelines.run_triage_batch data/sample-pdf
```

**Batch mode (all PDFs in `data/`):**

```bash
uv run python -m src.pipelines.run_triage_batch
```

### 2. Run Extraction (Stage 2)

**Single PDF:**

```bash
uv run python -m src.pipelines.run_extraction_batch .refinery/profiles/sample-pdf
```

**Batch mode:**

```bash
uv run python -m src.pipelines.run_extraction_batch
```

---

## Testing

Unit tests cover:

* TriageAgent classification (`origin_type`, `layout_complexity`, `domain_hint`)
* ExtractionRouter confidence-gated escalation
* FastText, Layout (Docling), and Vision strategies

Run all tests:

```bash
uv run python -m pytest
```

---

## Configuration

* **`rubric/extraction_rules.yaml`** – Thresholds for scanned vs native, table detection, and confidence gating
* **`.refinery/profiles/`** – Stores `DocumentProfile` JSONs
* **`.refinery/extraction_ledger.jsonl`** – Logs each extraction: strategy, confidence, cost, and processing time

---


