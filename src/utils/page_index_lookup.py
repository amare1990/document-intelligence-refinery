"""
PageIndex Lookup Utilities

Provides helpers for:

1. Loading a PageIndex from refinery artifacts
2. Finding the section path for a given page number
3. Navigating the PageIndex using a query
"""

# src/utils/page_index_lookup.py

import os
from dotenv import load_dotenv

import json
from pathlib import Path
from typing import List, Optional

from src.models.page_index import PageIndex, PageNode


load_dotenv(".env")

INDEX_DIR = Path(
    os.getenv("PAGE_INDEX_DIR", ".refinery/page_index")
)


# --------------------------------------------------
# Load PageIndex
# --------------------------------------------------

def load_page_index(doc_id: str) -> Optional[PageIndex]:
    """
    Load PageIndex artifact for a document.
    """

    path = INDEX_DIR / f"{doc_id}_page_index.json"

    if not path.exists():
        return None

    try:
        data = json.loads(path.read_text())
        return PageIndex(**data)
    except Exception:
        return None


# --------------------------------------------------
# Page → Section Path
# Used for provenance reconstruction
# --------------------------------------------------

def find_section_by_page(
    node: PageNode,
    page: int,
    path: List[str] | None = None
) -> List[str]:
    """
    Recursively locate the section path containing a page.
    """

    if path is None:
        path = []

    if not (node.page_start <= page <= node.page_end):
        return []

    new_path = path + [node.title]

    for child in node.children:
        result = find_section_by_page(child, page, new_path)
        if result:
            return result

    return new_path


# --------------------------------------------------
# Query → Relevant Sections
# Used by QueryAgent navigation
# --------------------------------------------------

def find_relevant_sections(
    node: PageNode,
    query: str,
    results: Optional[List[tuple[int, str]]] = None
) -> List[str]:

    if results is None:
        results = []

    q = query.lower()

    score = 0

    if q in (node.title or "").lower():
        score += 3

    if node.summary and q in node.summary.lower():
        score += 2

    if node.keywords:
        if any(q in kw.lower() for kw in node.keywords):
            score += 1

    if node.key_entities:
        if any(q in ent.lower() for ent in node.key_entities):
            score += 1

    if score > 0:
        results.append((score, node.title))

    for child in node.children:
        find_relevant_sections(child, query, results)

    # Only convert to List[str] at the root
    if node.title == "Document Root":
        results.sort(reverse=True)
        return [title for _, title in results]

    return []
