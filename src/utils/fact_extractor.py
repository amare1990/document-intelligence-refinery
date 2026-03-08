"""
Fact extractor for financial tables.
This is a simplified example. Real implementations would need to handle:
 - More complex table structures (merged cells, multi-line headers)
 - More robust measure normalization (synonyms, abbreviations)
 - More sophisticated numeric parsing (units, ranges)
"""


# src/utils/fact_extractor.py

import re
from typing import List


MEASURE_NORMALIZATION = {
    "total revenue": "revenue",
    "net revenue": "revenue",
    "sales": "revenue",
    "operating income": "income",
    "profit": "profit",
}


def normalize_measure(name: str) -> str:
    name = name.lower().strip()
    return MEASURE_NORMALIZATION.get(name, name)


def extract_numeric(value: str):
    match = re.search(r"[-+]?\d*\.?\d+", value.replace(",", ""))
    return float(match.group()) if match else None


def detect_period(text: str):
    year = re.search(r"\b(19|20)\d{2}\b", text)
    return year.group() if year else None


def extract_facts_from_table(
        doc_id: str,
        table_id: str,
        rows: List[List[str]],
        page: int,
        section: str,
        store,
    ):

    if not rows or len(rows) < 2:
        return

    headers = [h.strip() for h in rows[0]]

    for r_idx, row in enumerate(rows[1:], start=1):

        period = detect_period(" ".join(row))

        for c_idx, cell in enumerate(row):

            value = extract_numeric(cell)

            if value is None:
                continue

            measure = normalize_measure(headers[c_idx])

            store.insert_fact(
                doc_id=doc_id,
                table_id=table_id,
                row_index=r_idx,
                column_name=measure,
                value=value,
            )


def extract_facts_from_ldus(doc_id, ldus, store):

    for ldu in ldus:

        # detect table-like chunks
        if ldu.chunk_type != "table":
            continue

        rows = [r.split("|") for r in ldu.text.split("\n") if "|" in r]

        if len(rows) < 2:
            continue

        extract_facts_from_table(
            doc_id=doc_id,
            table_id=ldu.ldu_id,
            rows=rows,
            page=ldu.page_number,
            section=ldu.section_path[0] if ldu.section_path else "",
            store=store
        )

