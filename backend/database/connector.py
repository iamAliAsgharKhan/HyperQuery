# backend/database/connector.py
import sqlite3
from contextlib import contextmanager
from typing import List, Dict, Any, Tuple
from ..config import settings

class DatabaseConnector:
    def __init__(self):
        self.conn = None

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        self.conn = sqlite3.connect(
            settings.DATABASE_PATH,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        self.conn.row_factory = sqlite3.Row
        try:
            yield self.conn
        finally:
            self.conn.close()
            self.conn = None

    def execute_safe_query(self, query: str) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Execute a query with safety checks"""
        if not any(query.strip().upper().startswith(cmd) for cmd in settings.ALLOWED_OPERATIONS):
            raise ValueError(f"Only {settings.ALLOWED_OPERATIONS} queries are allowed")

        with self.get_connection() as conn:  # This now uses the context manager
            cursor = conn.cursor()
            try:
                cursor.execute(query)
                results = [dict(row) for row in cursor.fetchall()]
                columns = [column[0] for column in cursor.description] if cursor.description else []
                return results, columns
            except sqlite3.Error as e:
                raise RuntimeError(f"Database error: {str(e)}")