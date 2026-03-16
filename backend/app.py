from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import shutil
import uuid
import uvicorn
from pipelines.db_pipeline import run_db_query
from pipelines.csv_pipeline import run_csv_query
from utils.db import DBUtils

app = FastAPI(title="Universal Query Dashboard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db_utils = DBUtils()

class QueryRequest(BaseModel):
    question: str
    table_name: str
    session_id: str = "default"
    is_csv: bool = False
    csv_path: Optional[str] = None

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/tables")
async def get_tables():
    return {"tables": db_utils.get_all_tables()}

@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files allowed")
    
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"{uuid.uuid4()}_{file.filename}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {"file_path": file_path, "filename": file.filename}

@app.post("/query")
async def query(request: QueryRequest):
    try:
        if request.is_csv:
            if not request.csv_path:
                 raise HTTPException(status_code=400, detail="CSV path required for CSV query")
            result = await run_csv_query(request.csv_path, request.question)
        else:
            result = await run_db_query(request.question, request.table_name, request.session_id)
            
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
