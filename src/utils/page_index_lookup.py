"""
This module provides utilities for loading and querying page index information for documents.
The page index is stored as JSON files in a specified directory, with each file corresponding to a
 document and containing a hierarchical structure of sections and their associated page ranges.
 The module includes functions to load the page index for a given document ID and to find
 the section path for a specific page number within the document. The section path is represented
 as a list of section titles that lead to the specified page, allowing for a hierarchical
 understanding of where the page falls within the document's structure. This utility can be used
 in conjunction with other components of the system, such as the QueryAgent, to provide more
 context about the location of retrieved LDUs within the document's structure.
Note: The implementation assumes that the page index JSON files are structured in a specific way, with a root node containing the document ID and a hierarchical structure of sections. The actual structure of the PageIndex and PageNode classes should be defined in the src.models.page_index module, and the JSON files should be formatted accordingly for the functions to work correctly. The provided code is a basic implementation and can be extended or modified as needed to fit specific use cases or requirements of the application.
"""

# src/utils/page_index_lookup.py


import json
from pathlib import Path
from typing import List

from src.models.page_index import PageIndex, PageNode


INDEX_DIR = Path(".refinery/page_index")


def load_page_index(doc_id: str) -> PageIndex | None:

    path = INDEX_DIR / f"{doc_id}_page_index.json"

    if not path.exists():
        return None

    data = json.loads(path.read_text())
    return PageIndex(**data)


def find_section(node: PageNode, page: int, path: List[str]) -> List[str]:

    if not (node.page_start <= page <= node.page_end):
        return path

    new_path = path + [node.title]

    for child in node.children:
        result = find_section(child, page, new_path)
        if result:
            return result

    return new_path
