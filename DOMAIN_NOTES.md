
---

# DOMAIN_NOTES.md

## Document Intelligence Refinery

Enterprise document repositories contain heterogeneous documents including native PDFs, scanned reports, financial statements, technical papers, and slide decks. These documents encode critical knowledge but are difficult to analyze automatically due to structural complexity and inconsistent formatting.

The **Document Intelligence Refinery** is a multi-stage, agentic pipeline that transforms these documents into **structured, spatially-indexed, and queryable knowledge**. The system prioritizes **extraction fidelity**, **provenance preservation**, and **cost-efficient processing** by dynamically routing documents through multiple extraction strategies.

The architecture is designed to balance **accuracy, cost, and scalability**, ensuring that high-cost vision models are only used when simpler extraction techniques fail.

---

# 1. Document Class Taxonomy

Understanding document classes is essential because **different document types fail in different ways**.

| Document Class        | Typical Example                      | Structural Properties    | Extraction Risk |
| --------------------- | ------------------------------------ | ------------------------ | --------------- |
| Native Digital PDF    | Annual reports, research papers      | Embedded text stream     | Low             |
| Multi-column Layout   | Journals, magazines                  | Complex reading order    | Medium          |
| Table-heavy Documents | Financial statements                 | Dense tabular structures | Medium          |
| Scanned Documents     | Contracts, legacy archives           | Image-only               | High            |
| Hybrid Documents      | Slides or reports with images + text | Mixed modalities         | High            |

This taxonomy informs the **triage routing logic** used in the extraction stage.

---

# 2. Extraction Strategy Decision Tree

The system uses a **confidence-gated routing mechanism** to select the optimal extraction strategy.

```
                 +--------------------+
                 |   Document Input   |
                 +--------------------+
                           |
                           v
                    [Triage Agent]
       Detect: origin_type | layout_complexity | domain_hint | language
                           |
        -----------------------------------------------------
        |                     |                             |
Native Digital          Multi-column               Scanned/Image
Single Column           Table-heavy                No text stream
        |                     |                             |
        v                     v                             v
[Strategy A]            [Strategy B]                  [Strategy C]
Fast Text Extractor     Layout-Aware Extractor       Vision Extractor
(pdfplumber)            (Docling / MinerU)           (Gemini / GPT-4o)
        |                     |                             |
        +---------- Confidence Evaluation ------------------+
                           |
                   Escalate if Low
```

### Strategy Cost Hierarchy

| Strategy          | Cost     | Speed     | Accuracy               |
| ----------------- | -------- | --------- | ---------------------- |
| FastTextExtractor | Very Low | Very Fast | High (digital docs)    |
| LayoutExtractor   | Medium   | Moderate  | High (complex layouts) |
| VisionExtractor   | High     | Slow      | Highest (scanned docs) |

Routing ensures the system **minimizes cost while maintaining fidelity**.

---

# 3. Confidence-Gated Escalation Logic

Extraction confidence is estimated using:

* character density
* layout consistency
* table structure detection
* OCR reliability score

Example routing logic:

```
if confidence >= 0.85:
    accept result
elif 0.6 <= confidence < 0.85:
    escalate to layout extractor
else:
    escalate to vision extractor
```

This prevents **low-quality extractions from propagating downstream into RAG systems**, which would otherwise produce hallucinated answers.

---

# 4. Failure Modes Across Document Classes

| Failure Mode           | Document Class    | Root Cause                               | Mitigation                    |
| ---------------------- | ----------------- | ---------------------------------------- | ----------------------------- |
| Structure Collapse     | Multi-column PDFs | Linear text extraction ignores layout    | Layout-aware parsing          |
| OCR Noise              | Scanned docs      | Low-quality scan or handwriting          | Vision models                 |
| Table Fragmentation    | Financial reports | Tables extracted as plain text           | Table-aware layout extraction |
| Reading Order Errors   | Journals          | Column ordering lost                     | Layout graph reconstruction   |
| Numeric Precision Loss | Financial docs    | OCR confusion (1 vs l, comma vs decimal) | Table verification            |
| Caption Detachment     | Technical reports | Figures separated from captions          | Combine figure + caption LDU  |
| Reference Breakage     | Legal documents   | Cross-references lost during chunking    | Section-aware indexing        |

These observations motivated the **multi-strategy architecture** used in the pipeline.

---

# 5. Logical Document Units (LDUs)

Traditional RAG pipelines chunk text using fixed token windows. This breaks semantic structures such as:

* tables
* figure captions
* bullet lists
* section headers

Instead, the refinery produces **Logical Document Units (LDUs)**.

An LDU represents the **smallest semantically complete unit** of a document.

Example:

```
LDU:
  doc_id: annual_report
  page: 12
  type: table
  bbox: [x1, y1, x2, y2]
  text: Revenue grew 12% YoY
  content_hash: 9f3ab2...
```

Advantages:

* preserves structural meaning
* enables spatial referencing
* improves retrieval accuracy

---

# 6. Provenance and PageIndex

A core design goal is **verifiability**.

Each answer returned by the query agent includes:

* page number
* bounding box coordinates
* content hash
* extraction strategy used

This information forms a **ProvenanceChain**.

Example:

```
Query → LDU Match → PageIndex Section → Source Page
```

### Why PageIndex Matters

Vector search alone often retrieves semantically similar content but ignores document structure.

Example query:

> "What is the revenue growth in the financial overview section?"

Naive vector search may retrieve:

* footnotes
* unrelated tables
* appendix content

PageIndex improves accuracy by **constraining retrieval to relevant document sections**.

---

# 7. Cost-Aware Architecture

Vision models provide superior extraction accuracy but are **10–100× more expensive** than text-based methods.

Example approximate costs:

| Method            | Cost per Page |
| ----------------- | ------------- |
| Text extraction   | ~0.001        |
| Layout parsing    | ~0.01         |
| Vision extraction | ~0.10+        |

If a 200-page document used vision extraction for all pages, cost would increase dramatically.

The refinery instead uses **progressive escalation**:

```
Fast Text → Layout → Vision
```

Only pages with **low extraction confidence** trigger expensive vision processing.

This design reduces processing cost while maintaining accuracy.

---

# 8. Architecture Design Principles

The system follows several engineering principles:

### 1. Strategy Pattern

Extraction methods are implemented as interchangeable strategies.

```
BaseExtractor
 ├ FastTextExtractor
 ├ LayoutExtractor
 └ VisionExtractor
```

This allows new strategies to be added without modifying the pipeline.

---

### 2. Typed Data Contracts

All pipeline artifacts are defined using **Pydantic models**:

* DocumentProfile
* ExtractedDocument
* LDU
* PageIndex
* ProvenanceChain

Typed schemas ensure **validation and interoperability between stages**.

### 3. Final Pipeline Architecture

```bash
PDF
 │
 ▼
TriageAgent
 │
 ▼
ExtractorAgent
 │
 ▼
SemanticChunker
 │
 ▼
LDUs
 │
 ├── PageIndexBuilder
 │
 ├── VectorStore
 │
 └── FactTableStore
        │
        ▼
      QueryAgent
        │
        ▼
     AuditAgent
```
---

### 3. Configurable Routing

Extraction rules are externalized in:

```
rubric/extraction_rules.yaml
```

This allows **new document types to be supported without modifying code**.

---

# 9. Why This Architecture Matters

Enterprise document systems must satisfy three requirements:

1. **Accuracy** — Extract structured information faithfully.
2. **Traceability** — Every claim must map back to a source location.
3. **Cost Efficiency** — Processing large document corpora must remain affordable.

The Document Intelligence Refinery addresses all three through:

* adaptive extraction routing
* semantic chunking with LDUs
* hierarchical indexing with PageIndex
* provenance-preserving query responses

---

# Key Takeaways

1. Document extraction requires **adaptive strategies**, not a single OCR pipeline.
2. Logical Document Units preserve semantic meaning better than token chunking.
3. Provenance chains are essential for trustworthy document intelligence systems.
4. Cost-aware routing ensures scalable processing across large document corpora.

---
