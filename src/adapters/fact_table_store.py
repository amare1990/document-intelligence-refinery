
"""
FactTableStore: A simple SQLite-based store for structured facts extracted from documents.
"""""

# src/adapters/fact_table_store.py

import sqlite3


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

    # -----------------------------
    # INSERT FACT
    # -----------------------------

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
    # GENERIC SQL QUERY
    # -----------------------------

    def query(self, sql: str):

        cursor = self.conn.cursor()
        cursor.execute(sql)

        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    # -----------------------------
    # TYPED QUERY HELPERS
    # -----------------------------

    def total_revenue(self):

        cursor = self.conn.execute(
            """
            SELECT SUM(CAST(value AS FLOAT)) AS total
            FROM facts
            WHERE column_name='revenue'
            """
        )

        row = cursor.fetchone()
        return row["total"] if row else None

    def revenue_by_year(self, year: str):

        cursor = self.conn.execute(
            """
            SELECT *
            FROM facts
            WHERE column_name='revenue'
            """
        )

        rows = cursor.fetchall()

        # simple filtering since schema doesn't store year separately
        return [dict(r) for r in rows if year in str(r["value"])]
