import sqlite3
from typing import List, Dict, Any
import re

class QueryRunner:
    def __init__(self, db_path: str = 'data.db'):
        self.db_path = db_path
    
    def run_sql(self, sql_query: str, table_name: str) -> List[Dict[str, Any]]:
        """
        Safely execute a SQL query against the database.
        """
        # Validate the query is safe (only SELECT allowed)
        if not self._is_safe_query(sql_query):
            raise ValueError("Invalid query: Only SELECT statements are allowed")
        
        # Validate the query references the correct table
        if not self._references_correct_table(sql_query, table_name):
            raise ValueError(f"Query must reference table '{table_name}'")
        
        # Connect to database and execute query
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(sql_query)
            rows = cursor.fetchall()
            
            # Get column names
            column_names = [description[0] for description in cursor.description]
            
            # Convert to list of dictionaries
            result = []
            for row in rows:
                result.append(dict(zip(column_names, row)))
                
        except Exception as e:
            conn.close()
            raise e
        
        conn.close()
        return result
    
    def _is_safe_query(self, query: str) -> bool:
        """
        Check if the query is safe to execute (only allows SELECT).
        """
        # Remove comments and extra whitespace
        cleaned_query = re.sub(r'/\*.*?\*/', '', query, flags=re.DOTALL)
        cleaned_query = re.sub(r'--.*', '', cleaned_query)
        cleaned_query = ' '.join(cleaned_query.split())
        
        # Check if it starts with SELECT (case insensitive)
        return cleaned_query.upper().strip().startswith('SELECT')
    
    def _references_correct_table(self, query: str, table_name: str) -> bool:
        """
        Check if the query references the specified table.
        """
        # Simple check: table name should appear in the query
        # This is a basic check - in production, you'd want more sophisticated parsing
        return table_name.lower() in query.lower()