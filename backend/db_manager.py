import sqlite3
from typing import Dict, Any, List
import pandas as pd

class DBManager:
    def __init__(self, db_path: str = 'data.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database and create sample data if needed."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if we already have tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        if not existing_tables:
            # Create sample BMW vehicle inventory table if no tables exist
            self.create_sample_bmw_table(conn)
        
        conn.close()
    
    def create_sample_bmw_table(self, conn):
        """Create a sample BMW vehicle inventory table with dummy data."""
        cursor = conn.cursor()
        
        # Sample BMW data schema
        cursor.execute("""
            CREATE TABLE vehicles (
                VehicleID INTEGER PRIMARY KEY,
                Make TEXT,
                Model TEXT,
                Year INTEGER,
                FuelType TEXT,
                Price REAL,
                Mileage INTEGER,
                Color TEXT,
                Transmission TEXT,
                EngineSize REAL
            )
        """)
        
        # Insert sample data
        sample_data = [
            (1, 'BMW', '3 Series', 2022, 'Gasoline', 45000.0, 15000, 'Black', 'Automatic', 2.0),
            (2, 'BMW', '5 Series', 2021, 'Gasoline', 55000.0, 20000, 'White', 'Automatic', 3.0),
            (3, 'BMW', 'X3', 2023, 'Hybrid', 52000.0, 8000, 'Blue', 'Automatic', 2.0),
            (4, 'BMW', 'X5', 2022, 'Diesel', 65000.0, 12000, 'Silver', 'Automatic', 3.0),
            (5, 'BMW', 'M3', 2023, 'Gasoline', 85000.0, 5000, 'Red', 'Manual', 3.0),
            (6, 'BMW', 'X1', 2021, 'Gasoline', 40000.0, 25000, 'Gray', 'Automatic', 2.0),
            (7, 'BMW', 'Z4', 2022, 'Gasoline', 50000.0, 10000, 'Yellow', 'Automatic', 2.0),
            (8, 'BMW', 'iX', 2023, 'Electric', 75000.0, 3000, 'White', 'Automatic', 0.0),
            (9, 'BMW', '7 Series', 2022, 'Gasoline', 80000.0, 18000, 'Black', 'Automatic', 4.4),
            (10, 'BMW', 'X6', 2023, 'Hybrid', 70000.0, 7000, 'Blue', 'Automatic', 3.0),
            (11, 'BMW', '2 Series', 2021, 'Gasoline', 38000.0, 30000, 'Green', 'Manual', 2.0),
            (12, 'BMW', '4 Series', 2022, 'Gasoline', 48000.0, 12000, 'Purple', 'Automatic', 2.0),
            (13, 'BMW', 'i3', 2020, 'Electric', 42000.0, 22000, 'White', 'Automatic', 0.0),
            (14, 'BMW', 'X2', 2023, 'Gasoline', 43000.0, 6000, 'Orange', 'Automatic', 2.0),
            (15, 'BMW', '8 Series', 2022, 'Gasoline', 90000.0, 9000, 'Brown', 'Automatic', 4.4),
        ]
        
        cursor.executemany("""
            INSERT INTO vehicles VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_data)
        
        conn.commit()
    
    def get_table_names(self) -> List[str]:
        """Get all table names in the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return tables
    
    def get_table_schema(self, table_name: str) -> Dict[str, str]:
        """Get the schema of a specific table."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get column info
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        
        schema = {}
        for col in columns:
            # col[1] is column name, col[2] is type
            col_name = col[1]
            col_type = col[2]
            schema[col_name] = col_type
        
        conn.close()
        return schema
    
    def execute_query(self, query: str, table_name: str) -> List[Dict[str, Any]]:
        """Execute a read-only query on a specific table."""
        # Only allow SELECT statements for security
        query_lower = query.strip().lower()
        if not query_lower.startswith('select '):
            raise ValueError("Only SELECT statements are allowed")
        
        # Additional validation: ensure query only references the allowed table
        if table_name not in query:
            raise ValueError(f"Query must reference table '{table_name}'")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(query)
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