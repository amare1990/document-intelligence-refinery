
---

# Document Intelligence Refinery

A **production-grade, agent-driven document intelligence pipeline** that transforms heterogeneous documents (PDFs, scans, images) into **structured, queryable knowledge**.

The system applies a **multi-stage agent architecture** to classify documents, extract structured content, build semantic document units, and enable **retrieval-augmented querying with provenance verification**.

---

# Author

**Name:** Amare Kassa

**Email:** [amaremek@gmail.com](mailto:amaremek@gmail.com)

**LinkedIn:** [https://www.linkedin.com/in/amaremek/](https://www.linkedin.com/in/amaremek/)

---

# Overview

The **Document Intelligence Refinery** processes documents through a staged pipeline:

```
Document
   ↓
[1] Triage Agent
   ↓
[2] Multi-Strategy Extraction Router
   ↓
[3] Semantic Chunking Engine (LDUs)
   ↓
[4] PageIndex Builder
   ↓
[5] Vector Embedding + Retrieval
   ↓
[6] Query Agent + Audit Verification
```

Each stage produces structured artifacts stored in the `.refinery/` workspace for **traceability, auditing, and reproducibility**.

---

# Extraction Strategy Engine

The system uses **adaptive extraction strategies** depending on document characteristics.

| Strategy                      | Use Case              | Description                    |
| ----------------------------- | --------------------- | ------------------------------ |
| **FastTextExtractor**         | Native digital PDFs   | Fast text extraction           |
| **LayoutExtractor (Docling)** | Table-heavy documents | Layout-aware parsing           |
| **VisionExtractor**           | Scanned documents     | Vision-assisted OCR extraction |

A **confidence-gated router** escalates extraction automatically if the initial strategy fails.

All extraction attempts are logged in:

```
.refinery/extraction_ledger.jsonl
```

---

# Requirements

* Python **3.12+**
* `uv` package manager
* Linux / macOS recommended

Core libraries:

* `pydantic`
* `pytest`
* `pdfplumber`
* `sentence-transformers`
* `torch`
* `transformers`
* `docling` (layout extraction)

---

# Setup

## 1. Clone the Repository

```bash
git clone https://github.com/amare1990/document-intelligence-refinery.git
cd document-intelligence-refinery
```

---

# 2. Create Environment

```bash
uv venv
source .venv/bin/activate
```

---

# 3. Install Dependencies

```bash
uv sync
```

Optional layout extraction dependencies:

```bash
uv add git+https://github.com/DS4SD/docling.git
uv add torch transformers
```

---

# 4. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Then edit `.env` and insert your API keys:

```
GEMINI_API_KEY=your_actual_key_here

OPENAI_API_KEY=your_openai_api_key_here

```

---

# Project Structure

```
src/
│
├── agents/
│   ├── triage.py
│   ├── extractor.py
│   ├── indexer.py
│   ├── query_agent.py
│   └── audit_agent.py
│
├── models/
│   ├── document_profile.py
│   ├── extracted_document.py
│   ├── ldu.py
│   ├── page_index.py
│   ├── provenance_chain.py
│   └── audit_result.py
│
├── adapters/
│   ├── embedding_store.py
│   └── fact_table_store.py
│
├── strategies/
│   ├── fast_text_extractor.py
│   ├── layout_extractor.py
│   └── vision_extractor.py
│
├── pipelines/
│   ├── run_triage_batch.py
│   ├── run_extraction_batch.py
│   ├── run_chunking.py
│   ├── run_page_index.py
│   ├── run_build_vector_index.py
│   ├── run_query_agent_semantic.py
│   └── run_refinery_pipeline.py
│
└── utils/
    ├── pdf_stats.py
    ├── language.py
    ├── ledger.py
    └── page_index_lookup.py
```

---

# Refinery Workspace

The pipeline generates artifacts in the `.refinery/` directory.

```
.refinery/
│
├── profiles/
├── extractions/
├── ldus/
├── page_index/
└── extraction_ledger.jsonl
```

These artifacts allow **reproducible document analysis**.

---

# Usage

Assume a document:

```
data/sample.pdf
```

---

# Stage 1 — Run Triage

Analyze document characteristics.

Single document:

```bash
uv run python -m src.pipelines.run_triage_batch data/sample.pdf
```

Batch mode:

```bash
uv run python -m src.pipelines.run_triage_batch
```

Output:

```
.refinery/profiles/
```

---

# Stage 2 — Run Extraction

Single document:

```bash
uv run python -m src.pipelines.run_extraction_batch data/sample.pdf
```

Batch mode:

```bash
uv run python -m src.pipelines.run_extraction_batch
```

Output:

```
.refinery/extractions/
```

---

# Stage 3 — Semantic Chunking (LDUs)

Generate **Logical Document Units**.

Single document:

```bash
uv run python -m src.pipelines.run_chunking \
--extraction ".refinery/extractions/document_extracted.json"
```

Batch mode:

```bash
uv run python -m src.pipelines.run_chunking --batch
```

Output:

```
.refinery/ldus/
```

---

# Stage 4 — Build Page Index

Creates hierarchical document navigation.

Single document:

```bash
uv run python -m src.pipelines.run_page_index \
--ldu_file ".refinery/ldus/doc_ldus.json"
```

Batch mode:

```bash
uv run python -m src.pipelines.run_page_index --batch
```

Output:

```
.refinery/page_index/
```

---

# Stage 5 — Build Vector Index

Generate embeddings for semantic search.

```bash
uv run python -m src.pipelines.run_build_vector_index \
--extraction ".refinery/extractions/document_extracted.json"
```

---

# Stage 6 — Query Agent

Run semantic queries against the document.

```bash
uv run python -m src.pipelines.run_query_agent_semantic \
  --query "Expired ROUA" \
  --extractions-dir ".refinery/extractions" \
  --pageindex-dir ".refinery/page_index" \
  --top-k 5
```

---

# Run Full Pipeline

Process a document end-to-end.

```bash
uv run python -m src.pipelines.run_refinery_pipeline \
    --pdf data/financial_report.pdf
```

Run pipeline with query:

```bash
uv run python -m src.pipelines.run_refinery_pipeline \
    --pdf data/financial_report.pdf \
    --query "What was the revenue growth?"
```

---

# Testing

Run all unit tests:

```bash
uv run python -m pytest
```

Tests cover:

* Triage classification
* Extraction strategy routing

---

# Configuration

Key configuration files:

```
rubric/extraction_rules.yaml
```

Defines:

* scanned vs native thresholds
* table detection rules
* confidence gating thresholds

---

# Key Features

* Agent-driven document processing
* Multi-strategy extraction engine
* Confidence-gated strategy escalation
* Semantic chunking (LDUs)
* Hierarchical page indexing
* Retrieval-augmented querying
* Evidence verification via Audit Agent
* Full pipeline reproducibility

---

# License

MIT License

---

