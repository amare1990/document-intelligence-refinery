"""
# Page Index Builder
# This module defines the PageIndexBuilder class, which constructs a hierarchical page index from the extracted document's LDUs. The page index organizes content by sections and their corresponding page ranges,
# src/agents/page_index_builder.py
"""

import uuid
from typing import Dict

from src.models.page_index import PageIndex, PageNode
from src.models.extracted_document import ExtractedDocument


class PageIndexBuilder:

    def build(self, extracted_doc: ExtractedDocument) -> PageIndex:

        root = PageNode(
            node_id=str(uuid.uuid4()),
            title="Document Root",
            page_start=1,
            page_end=999,
            children=[]
        )

        section_map: Dict[str, PageNode] = {}

        for ldu in extracted_doc.ldus:

            if not ldu.section_path:
                continue

            section = ldu.section_path[0]

            if section not in section_map:

                node = PageNode(
                    node_id=str(uuid.uuid4()),
                    title=section,
                    page_start=ldu.page_number,
                    page_end=ldu.page_number,
                    children=[]
                )

                section_map[section] = node
                root.children.append(node)

        return PageIndex(
            doc_id=extracted_doc.doc_id,
            root=root
        )
