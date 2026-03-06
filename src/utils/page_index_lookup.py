"""
PageIndex Lookup Utilities

Provides helpers for:

1. Loading a PageIndex from refinery artifacts
2. Finding the section path for a given page number
3. Navigating the PageIndex using a query
"""

import json
from pathlib import Path
from typing import List, Optional

from src.models.page_index import PageIndex, PageNode


INDEX_DIR = Path(".refinery/page_index")


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
    results: Optional[List[str]] = None
) -> List[str]:
    """
    Traverse the PageIndex tree and find sections relevant
    to a query using title/summary/keywords matching.
    """

    if results is None:
        results = []

    q = query.lower()

    searchable_text = " ".join([
        node.title or "",
        node.summary or "",
        " ".join(node.keywords) if node.keywords else ""
    ]).lower()

    if q in searchable_text:
        results.append(node.title)

    for child in node.children:
        find_relevant_sections(child, query, results)

    return results
