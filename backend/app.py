import sys
import os

from dotenv import load_dotenv
load_dotenv()

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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
from utils.auth import init_auth_db, create_user, authenticate_user

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Initialize the authentication database on startup
init_auth_db()

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Universal Query Dashboard",
    description="Agentic Analytics System with Natural Language Query Processing",
    version="2.0.0"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Validate environment
if not os.getenv("GEMINI_API_KEY") and not os.getenv("GOOGLE_API_KEY") and not os.getenv("HACKATHON_API_KEYS"):
    print("\nERROR: GEMINI_API_KEY or HACKATHON_API_KEYS is not set in environment variables.")
    print("Please create a .env file or set the variable to continue.\n")

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

class SignupRequest(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

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

@app.post("/auth/signup")
async def register(req: SignupRequest):
    """Register a new user account."""
    result = create_user(req.name, req.email, req.password)
    if result.get("success"):
        return result
    else:
        raise HTTPException(status_code=400, detail=result.get("error"))

@app.post("/auth/login")
async def auth_login(req: LoginRequest):
    """Log a user into their account."""
    result = authenticate_user(req.email, req.password)
    if result.get("success"):
        return result
    else:
        raise HTTPException(status_code=401, detail=result.get("error"))

@app.post("/upload-csv")
@limiter.limit("5/minute")
async def upload_csv(request: Request, file: UploadFile = File(...)):
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
            # content is bytes from await file.read()
            buffer.write(content) # type: ignore
            
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
@limiter.limit("15/minute")
async def query(request: Request, payload: QueryRequest):
    """Process natural language query and return results."""
    start_time = time.time()
    
    try:
        # Validate request
        if not payload.question or not payload.question.strip():
            return handle_validation_error(
                "Query question cannot be empty",
                field="question",
                value=payload.question
            )
        
        if not payload.is_csv and not payload.table_name:
            return handle_validation_error(
                "Table name is required for database queries",
                field="table_name",
                value=payload.table_name
            )
        
        # Process query
        if payload.is_csv:
            if not payload.csv_path:
                return handle_validation_error(
                    "CSV path is required for CSV queries",
                    field="csv_path",
                    value=payload.csv_path
                )
            result = await run_csv_query(payload.csv_path, payload.question, payload.session_id)
        else:
            result = await run_db_query(payload.question, payload.table_name, payload.session_id)
        
        # Add performance metrics
        execution_time: float = time.time() - start_time
        result["execution_time_ms"] = float(f"{execution_time * 1000:.2f}")
        result["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Log performance metric
        ErrorHandler.log_performance_metric(
            operation="query_processing",
            duration=execution_time,
            success=result.get("success", False),
            details={
                "question_length": len(payload.question),
                "is_csv": payload.is_csv,
                "table_name": payload.table_name,
                "session_id": payload.session_id
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
                "question_length": len(payload.question) if payload.question else 0,
                "is_csv": payload.is_csv,
                "table_name": payload.table_name
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
