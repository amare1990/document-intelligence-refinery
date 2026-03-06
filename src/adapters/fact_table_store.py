
# FactTableStore: A simple SQLite-based store for structured facts extracted from documents.
# src/adapters/fact_table_store.py

import sqlite3
from pathlib import Path


class FactTableStore:

    def __init__(self, db_path: str = ".refinery/facts.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):

        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS facts (
                doc_id TEXT,
                table_id TEXT,
                row_index INTEGER,
                column_name TEXT,
                value TEXT
            )
            """
        )

        self.conn.commit()

    def insert_fact(self, doc_id, table_id, row_index, column_name, value):

        self.conn.execute(
            """
            INSERT INTO facts
            VALUES (?, ?, ?, ?, ?)
            """,
            (doc_id, table_id, row_index, column_name, value),
        )

        self.conn.commit()

    # -----------------------------
    # NEW: Structured Query Method
    # -----------------------------

    def query(self, sql: str):

        cursor = self.conn.cursor()
        cursor.execute(sql)

        rows = cursor.fetchall()

        return [dict(row) for row in rows]
