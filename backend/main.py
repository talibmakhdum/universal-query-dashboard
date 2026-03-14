from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import sqlite3
import pandas as pd
import os
from db_manager import DBManager
from gemini import GeminiProcessor
from query_runner import QueryRunner
from chart_picker import ChartPicker
import tempfile

app = FastAPI(title="Universal Query Dashboard API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
db_manager = DBManager()
gemini_processor = GeminiProcessor()
query_runner = QueryRunner()
chart_picker = ChartPicker()

class QueryRequest(BaseModel):
    question: str
    tableName: str
    history: List[Dict[str, str]] = []

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a CSV file and create a new table in the database.
    Returns the table name and schema.
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only")
        
        # Validate file size (max 10MB)
        contents = await file.read()
        if len(contents) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(status_code=400, detail="File too large (max 10MB)")
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
            tmp_file.write(contents)
            temp_path = tmp_file.name
        
        try:
            # Read CSV and create table
            df = pd.read_csv(temp_path)
            
            # Generate unique table name
            table_name = f"uploaded_{len(db_manager.get_table_names()) + 1}"
            
            # Create table and insert data
            conn = sqlite3.connect('data.db')
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            conn.close()
            
            # Get schema
            schema = db_manager.get_table_schema(table_name)
            
            return {
                "tableName": table_name,
                "schema": schema
            }
        finally:
            # Clean up temporary file
            os.unlink(temp_path)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/api/query")
async def query_data(request: QueryRequest):
    """
    Process a natural language query and return visualization data.
    """
    try:
        # Validate table exists
        if request.tableName not in db_manager.get_table_names():
            raise HTTPException(status_code=400, detail="Table does not exist")
        
        # Get table schema
        schema = db_manager.get_table_schema(request.tableName)
        
        # Convert natural language to SQL
        sql_query = gemini_processor.nl_to_sql(
            question=request.question,
            table_name=request.tableName,
            schema=schema,
            history=request.history
        )
        
        if sql_query == "CANNOT_ANSWER":
            return {
                "success": False,
                "error": "Unable to understand the query. Please try rephrasing.",
                "chartType": "bar"
            }
        
        # Execute the SQL query
        results = query_runner.run_sql(sql_query, request.tableName)
        
        if not results:
            return {
                "success": False,
                "error": "No results found for the query.",
                "chartType": "bar"
            }
        
        # Determine chart type
        chart_type = chart_picker.pick_chart_type(results, schema)
        
        # Generate insight
        insight = gemini_processor.generate_insight(results)
        
        return {
            "success": True,
            "data": results,
            "chartType": chart_type,
            "insight": insight,
            "sql": sql_query
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"An error occurred: {str(e)}",
            "chartType": "bar"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)