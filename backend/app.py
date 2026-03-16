from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import shutil
import uuid
import uvicorn
import time
import uuid
from pipelines.db_pipeline import run_db_query
from pipelines.csv_pipeline import run_csv_query
from utils.db import DBUtils
from utils.error_handler import (
    ErrorHandler, handle_query_error, handle_validation_error, 
    handle_database_error, handle_security_error, handle_agent_error
)
from utils.monitoring import (
    start_monitoring, stop_monitoring, record_query_start, record_query_end, 
    get_health_status, get_performance_stats
)

app = FastAPI(
    title="Universal Query Dashboard",
    description="Agentic Analytics System with Natural Language Query Processing",
    version="2.0.0"
)

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

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    uptime: str

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to all responses."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint with system status."""
    return {
        "status": "healthy",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "version": "2.0.0",
        "uptime": "system_running"
    }

@app.get("/tables")
async def get_tables():
    """Get available database tables."""
    try:
        tables = db_utils.get_all_tables()
        return {
            "success": True,
            "tables": tables,
            "count": len(tables)
        }
    except Exception as e:
        return handle_database_error(f"Failed to retrieve tables: {str(e)}")

@app.get("/system-info")
async def get_system_info():
    """Get system information and capabilities."""
    return {
        "success": True,
        "system": {
            "name": "Universal Query Dashboard",
            "version": "2.0.0",
            "architecture": "Agentic Analytics System",
            "capabilities": [
                "Natural Language Query Processing",
                "Multi-Agent SQL Generation",
                "CSV Analysis Pipeline",
                "Auto Chart Generation",
                "Conversation Memory",
                "Security Validation"
            ],
            "supported_formats": ["SQLite", "CSV"],
            "features": {
                "self_correcting": True,
                "context_aware": True,
                "real_time_processing": True,
                "error_handling": True
            }
        }
    }

@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    """Upload CSV file for analysis."""
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            return handle_validation_error(
                "Only CSV files are supported for upload",
                field="file",
                value=file.filename
            )
        
        # Validate file size (limit to 50MB)
        content = await file.read()
        if len(content) > 50 * 1024 * 1024:  # 50MB limit
            return handle_validation_error(
                "File size exceeds 50MB limit",
                field="file_size",
                value=f"{len(content) / (1024*1024):.2f}MB"
            )
        
        # Create upload directory
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, f"{uuid.uuid4()}_{file.filename}")
        
        # Save file
        with open(file_path, "wb") as buffer:
            buffer.write(content)
            
        return {
            "success": True,
            "file_path": file_path,
            "filename": file.filename,
            "size": f"{len(content) / 1024:.2f}KB",
            "message": f"Successfully uploaded {file.filename}"
        }
        
    except Exception as e:
        return handle_database_error(f"Failed to upload CSV file: {str(e)}")

@app.post("/query")
async def query(request: QueryRequest):
    """Process natural language query and return results."""
    start_time = time.time()
    
    try:
        # Validate request
        if not request.question or not request.question.strip():
            return handle_validation_error(
                "Query question cannot be empty",
                field="question",
                value=request.question
            )
        
        if not request.is_csv and not request.table_name:
            return handle_validation_error(
                "Table name is required for database queries",
                field="table_name",
                value=request.table_name
            )
        
        # Process query
        if request.is_csv:
            if not request.csv_path:
                return handle_validation_error(
                    "CSV path is required for CSV queries",
                    field="csv_path",
                    value=request.csv_path
                )
            result = await run_csv_query(request.csv_path, request.question)
        else:
            result = await run_db_query(request.question, request.table_name, request.session_id)
        
        # Add performance metrics
        execution_time = time.time() - start_time
        result["execution_time_ms"] = round(execution_time * 1000, 2)
        result["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Log performance metric
        ErrorHandler.log_performance_metric(
            operation="query_processing",
            duration=execution_time,
            success=result.get("success", False),
            details={
                "question_length": len(request.question),
                "is_csv": request.is_csv,
                "table_name": request.table_name,
                "session_id": request.session_id
            }
        )
        
        return result
        
    except Exception as e:
        execution_time = time.time() - start_time
        
        # Log performance metric for failed requests
        ErrorHandler.log_performance_metric(
            operation="query_processing",
            duration=execution_time,
            success=False,
            details={
                "error": str(e),
                "question_length": len(request.question) if request.question else 0,
                "is_csv": request.is_csv,
                "table_name": request.table_name
            }
        )
        
        # Handle specific error types
        if "security" in str(e).lower() or "forbidden" in str(e).lower():
            return handle_security_error(f"Security violation in query: {str(e)}")
        elif "database" in str(e).lower() or "connection" in str(e).lower():
            return handle_database_error(f"Database error: {str(e)}")
        elif "agent" in str(e).lower() or "llm" in str(e).lower():
            return handle_agent_error(f"Agent processing error: {str(e)}")
        else:
            return handle_query_error(f"Query processing failed: {str(e)}")

@app.post("/clear-session")
async def clear_session(session_id: str):
    """Clear conversation history for a specific session."""
    try:
        from memory.session_memory import memory_manager
        memory_manager.clear_session(session_id)
        return {
            "success": True,
            "message": f"Session {session_id} cleared successfully",
            "session_id": session_id
        }
    except Exception as e:
        return handle_query_error(f"Failed to clear session: {str(e)}")

@app.get("/session-stats/{session_id}")
async def get_session_stats(session_id: str):
    """Get statistics for a specific session."""
    try:
        from memory.session_memory import memory_manager
        summary = memory_manager.get_session_summary(session_id)
        return {
            "success": True,
            "session_id": session_id,
            "summary": summary
        }
    except Exception as e:
        return handle_query_error(f"Failed to get session stats: {str(e)}")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    return JSONResponse(
        status_code=500,
        content=handle_query_error(f"Unhandled server error: {str(exc)}")
    )

if __name__ == "__main__":
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info",
        access_log=True
    )
