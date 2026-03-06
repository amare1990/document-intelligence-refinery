"""
This module defines the VectorStore class, which provides an interface to a vector database
for storing and retrieving LDUs based on their content. The VectorStore class uses the
ChromaDB library to manage the vector database, allowing for efficient storage and retrieval
of LDUs based on their textual content. The class includes methods for adding LDUs to the database
and searching for relevant LDUs based on a query. Each LDU is stored with its text, a unique identifier,
and metadata that includes the document ID, page number, and content hash. The search method
retrieves the most relevant LDUs based on the query text and returns the results in a structured format.
The VectorStore class is designed to be used as part of a larger system for managing and retrieving
document content, providing a scalable and efficient way to handle large volumes of LDUs.
Note: The implementation assumes that the LDU objects have attributes such as text, ldu_id, doc_id,
page_number, and content_hash.
The actual structure of the LDU class is not defined in this module and should be implemented separately.
The VectorStore class provides a simple interface for interacting with the vector database, abstracting away
the complexities of managing the database and allowing for easy integration into other components of the system.
The use of ChromaDB ensures that the vector database is optimized for performance and scalability, making it
suitable for handling large datasets of LDUs.
Overall, the VectorStore class serves as a crucial component in the system for managing and retrieving document content,
providing an efficient and scalable solution for storing and retrieving LDUs based on their textual content.
Note: The actual implementation of the VectorStore class may require additional error handling, logging,
and configuration options depending on the specific requirements of the application. The provided code is
a basic implementation and can be extended or modified as needed to fit the specific use case.
# src/adapters/vector_store.py
"""

import chromadb


class VectorStore:

    def __init__(self):

        self.client = chromadb.Client()

        self.collection = self.client.get_or_create_collection(
            name="document_ldus"
        )


    def add_ldu(self, ldu):

        self.collection.add(
            documents=[ldu.text],
            ids=[ldu.ldu_id],
            metadatas=[{
                "doc_id": ldu.doc_id,
                "page": ldu.page_number,
                "hash": ldu.content_hash
            }]
        )


    def search(self, query, k=5):

        return self.collection.query(
            query_texts=[query],
            n_results=k
        )
