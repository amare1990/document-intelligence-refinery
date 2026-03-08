"""
# LDUVectorStore: A vector store for LDU embeddings using FAISS and OpenAI API
# This module defines the LDUVectorStore class, which provides an interface for storing and retrieving LDUs based on their embeddings. The class uses the OpenAI API to generate embeddings for LDU text and FAISS to manage the vector index for efficient similarity search. The LDUVectorStore class includes methods for adding LDUs to the store, searching for relevant LDUs based on a query,
# and saving/loading the vector index and metadata to/from disk. The implementation assumes that the LDU class is defined in the src.models.ldu module and includes attributes such as text, ldu_id, doc_id, page_number, and content_hash. The vector index is stored in a specified directory, and the metadata for the LDUs is saved as a JSON file for easy retrieval during search operations. The LDUVectorStore class serves as a crucial component in the system for managing and retrieving document content based on semantic similarity, providing an efficient and scalable solution for handling large volumes of LDUs.
# Note: The actual implementation of the LDUVectorStore class may require additional error handling, logging, and configuration options depending on the specific requirements of the application. The provided code is a basic implementation and can be extended or modified as needed to fit the specific use case.
"""

# src/adapters/embedding_store.py

import os
import json
import faiss
import numpy as np
from pathlib import Path
from typing import List

from openai import OpenAI
from src.models.ldu import LDU

from dotenv import load_dotenv
load_dotenv()

VECTOR_DIR = Path(".refinery/vector_store")
VECTOR_DIR.mkdir(parents=True, exist_ok=True)

INDEX_FILE = VECTOR_DIR / "faiss.index"
META_FILE = VECTOR_DIR / "ldu_metadata.json"



class LDUVectorStore:

    def __init__(self, dim: int = 1536):

        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment.")

        # client should ONLY be OpenAI
        self.client: OpenAI = OpenAI(api_key=api_key)

        self.dim = dim

        self.ids: List[str] = []
        self.ldus: List[LDU] = []

        if INDEX_FILE.exists():
            self.index = faiss.read_index(str(INDEX_FILE))
            self._load_metadata()
        else:
            self.index = faiss.IndexFlatL2(dim)

    def embed_text(self, text: str) -> np.ndarray:

        resp = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )

        return np.array(resp.data[0].embedding, dtype=np.float32)

    def add_ldus(self, ldus: List[LDU]):

        vectors = []
        metadata_records = []

        for ldu in ldus:

            emb = self.embed_text(
                f"{ldu.section_path} :: {ldu.text}"
            )

            vectors.append(emb)

            metadata_records.append({
                "ldu_id": ldu.ldu_id,
                "doc_id": ldu.doc_id,
                "chunk_type": ldu.chunk_type,
                "parent_section": ldu.section_path[0] if ldu.section_path else None,
                "page_refs": [ldu.page_number],
                "content_hash": ldu.content_hash
            })

            self.ids.append(ldu.ldu_id)
            self.ldus.append(ldu)

        if vectors:
            matrix = np.vstack(vectors).astype(np.float32)
            self.index.add(matrix) # type: ignore

        if META_FILE.exists():
            existing = json.loads(META_FILE.read_text())
        else:
            existing = []

        existing.extend(metadata_records)

        META_FILE.write_text(json.dumps(existing, indent=2))


    def search(self, query: str, top_k: int = 5):

        if self.index.ntotal == 0:
            return []

        q_emb = self.embed_text(query).reshape(1, -1)

        distances, indices = self.index.search(q_emb, top_k)  # type: ignore

        results = []

        for idx, i in enumerate(indices[0]):

            if i == -1:
                continue

            if i >= len(self.ldus):
                continue

            results.append((self.ldus[i], float(distances[0][idx])))

        return results

    def save(self):
        faiss.write_index(self.index, str(INDEX_FILE))


    def _load_metadata(self):

        if not META_FILE.exists():
            return

        data = json.loads(META_FILE.read_text())

        self.ldus = [LDU(**d) for d in data]
        self.ids = [ldu.ldu_id for ldu in self.ldus]

        if self.index.ntotal != len(self.ldus):
            print("Warning: FAISS index and metadata mismatch")
