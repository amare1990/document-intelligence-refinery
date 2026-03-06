"""
Stage 4 — PageIndex Builder

Builds a hierarchical navigation structure over the document
(similar to a smart table of contents).

Each section node contains:
- title
- page_start
- page_end
- summary (LLM generated)
"""

import os
import uuid
from typing import Dict, List

from dotenv import load_dotenv
from google import genai

from src.models.page_index import PageIndex, PageNode
from src.models.extracted_document import ExtractedDocument

load_dotenv()

# Initialize Gemini client once
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=api_key)
MODEL_ID = "gemini-2.0-flash"


def generate_summary(text: str) -> str:
    """
    Generate a short section summary using Gemini Flash.
    """

    prompt = f"""
Summarize the following document section in 2 concise sentences.

{text[:4000]}
"""

    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt,
    )

    if response.text:
        return response.text.strip()

    return "Summary unavailable."


class PageIndexer:
    """
    Builds a PageIndex tree from document LDUs.
    """

    def build(self, extracted_doc: ExtractedDocument) -> PageIndex:

        root = PageNode(
            node_id=str(uuid.uuid4()),
            title="Document Root",
            page_start=1,
            page_end=1,
            children=[]
        )

        section_map: Dict[str, PageNode] = {}
        section_text: Dict[str, List[str]] = {}

        for ldu in extracted_doc.ldus:

            if not ldu.section_path:
                continue

            section = ldu.section_path[0]

            # Collect text for summary generation
            section_text.setdefault(section, []).append(ldu.text)

            if section not in section_map:

                node = PageNode(
                    node_id=str(uuid.uuid4()),
                    title=section,
                    page_start=ldu.page_number,
                    page_end=ldu.page_number,
                    children=[],
                    summary=None,
                    keywords=[]
                )

                section_map[section] = node
                root.children.append(node)

            else:
                # update page range
                node = section_map[section]
                node.page_end = max(node.page_end, ldu.page_number)

        # Generate summaries for each section
        for section, node in section_map.items():

            combined_text = "\n".join(section_text.get(section, []))

            try:
                node.summary = generate_summary(combined_text)
            except Exception:
                node.summary = "Summary unavailable."

        return PageIndex(
            doc_id=extracted_doc.doc_id,
            root=root
        )
