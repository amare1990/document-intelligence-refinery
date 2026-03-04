# src/models/page_index.py
from pydantic import BaseModel, Field
from typing import List, Optional


class PageNode(BaseModel):
    """
    Node in the hierarchical document tree.

    Enables fast navigation before vector search.
    """

    node_id: str
    title: str

    page_start: int
    page_end: int

    summary: Optional[str] = None
    keywords: List[str] = []

    children: List["PageNode"] = []


PageNode.model_rebuild()


class PageIndex(BaseModel):
    """
    Table-of-contents style navigation index for an entire document.
    """

    doc_id: str
    root: PageNode
