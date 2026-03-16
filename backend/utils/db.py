from typing import List, Dict, Any, Optional
import sqlite3
import os

class DBUtils:
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Default to data.db in the backend directory
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.db_path = os.path.join(base_dir, 'data.db')
        else:
            self.db_path = db_path
            
    def get_table_schema(self, table_name: str) -> str:
        """Returns a string representation of the table schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        conn.close()
        
        schema_parts = []
        for col in columns:
            schema_parts.append(f"{col[1]} ({col[2]})")
        return ", ".join(schema_parts)

    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Executes a SQL query and returns results as dynamic dictionaries."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def get_all_tables(self) -> List[str]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall() if not row[0].startswith('sqlite_')]
        conn.close()
        return tables
