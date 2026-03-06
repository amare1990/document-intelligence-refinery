"""
# This script builds a vector index from a list of LDUs (Language Data Units) and saves it to disk.
# It reads LDUs from a specified JSON file, generates embeddings for each LDU using the OpenAI API,
# and stores the embeddings in a FAISS index for efficient similarity search. The metadata for each LDU is also saved to a JSON file for later retrieval during search operations. This script is intended to be run after the LDUs have been generated and saved by the chunking process, and it prepares the data for use in the query agent when retrieving relevant LDUs based on user queries.
# Note: The actual implementation of the LDU class and the structure of the input JSON file should be defined in the src.models.ldu module, and the input JSON file should be formatted accordingly for the script to work correctly. The provided code is a basic implementation and can be extended or modified as needed to fit specific use cases or requirements of the application.
"""
# run_build_vector_index.py

import os
import json
import argparse
from pathlib import Path

from dotenv import load_dotenv

from src.adapters.embedding_store import LDUVectorStore
from src.models.ldu import LDU

load_dotenv(".env")

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--ldus", required=True)

    args = parser.parse_args()

    path = Path(args.ldus)

    data = json.loads(path.read_text())

    ldus = [LDU(**l) for l in data]

    # api_key = input("Enter OpenAI API Key: ")
    api_key = os.getenv("OPENAI_API_KEY")

    store = LDUVectorStore()

    print(f"Embedding {len(ldus)} LDUs...")

    store.add_ldus(ldus)

    store.save()

    print("Vector index saved.")


if __name__ == "__main__":
    main()
