import time
import sqlite3
import re
import random
import threading
from typing import Optional
from agents.state import AgentState
from utils.db import DBUtils

class Executor:
    def __init__(self, max_retries: int = 3, timeout_seconds: int = 30):
        self.db = DBUtils()
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds
        
        # Retry delay configuration (exponential backoff with jitter)
        self.base_delay = 1.0
        self.max_delay = 10.0

    def execute(self, state: AgentState) -> AgentState:
        state["thought_process"].append("Executor: Running query on database...")
        
        # Validate SQL query before execution
        validation_error = self._validate_query(state["sql_query"])
        if validation_error:
            state["error"] = validation_error
            state["thought_process"].append(f"Executor Validation Error: {validation_error}")
            return state
        
        # Attempt execution with retry logic
        for attempt in range(self.max_retries):
            try:
                results = self._execute_with_timeout(state["sql_query"])
                
                # Validate results
                if results is None:
                    state["error"] = "Query executed but returned no results"
                    state["thought_process"].append("Executor: Query returned no results")
                    return state
                
                state["result"] = results
                state["error"] = None
                state["thought_process"].append(f"Executor: Successfully retrieved {len(results)} rows in attempt {attempt + 1}")
                return state
                
            except sqlite3.Error as e:
                error_msg = str(e)
                state["thought_process"].append(f"Executor Database Error (attempt {attempt + 1}): {error_msg}")
                
                if attempt < self.max_retries - 1:
                    delay = self._calculate_delay(attempt)
                    state["thought_process"].append(f"Executor: Retrying in {delay:.1f} seconds...")
                    time.sleep(delay)
                else:
                    state["error"] = f"Database error after {self.max_retries} attempts: {error_msg}"
                    
            except TimeoutError:
                state["thought_process"].append(f"Executor: Query timed out after {self.timeout_seconds} seconds (attempt {attempt + 1})")
                
                if attempt < self.max_retries - 1:
                    delay = self._calculate_delay(attempt)
                    state["thought_process"].append(f"Executor: Retrying in {delay:.1f} seconds...")
                    time.sleep(delay)
                else:
                    state["error"] = f"Query execution timed out after {self.max_retries} attempts"
                    
            except Exception as e:
                error_msg = str(e)
                state["thought_process"].append(f"Executor Unexpected Error (attempt {attempt + 1}): {error_msg}")
                
                if attempt < self.max_retries - 1:
                    delay = self._calculate_delay(attempt)
                    state["thought_process"].append(f"Executor: Retrying in {delay:.1f} seconds...")
                    time.sleep(delay)
                else:
                    state["error"] = f"Unexpected error after {self.max_retries} attempts: {error_msg}"
        
        return state

    def _validate_query(self, sql: str) -> Optional[str]:
        """Validate SQL query before execution."""
        if not sql or not sql.strip():
            return "Empty SQL query provided"
        
        sql_upper = sql.upper().strip()
        
        # Check for SELECT statement
        if not sql_upper.startswith("SELECT"):
            return "Only SELECT statements are allowed"
        
        # Check for potential infinite loops or heavy operations
        if "LIMIT" not in sql_upper and "WHERE" not in sql_upper:
            # This is a heuristic - some SELECT * queries might be valid
            pass
        
        # Check for suspicious patterns
        suspicious_patterns = [
            r"SELECT\s+\*\s+FROM\s+\w+\s+WHERE\s+1\s*=\s*1",
            r"SELECT\s+\*\s+FROM\s+\w+\s+WHERE\s+0\s*=\s*0",
            r"SELECT\s+\*\s+FROM\s+\w+\s+WHERE\s+TRUE",
            r"SELECT\s+\*\s+FROM\s+\w+\s+WHERE\s+FALSE"
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, sql_upper, re.IGNORECASE):
                return "Query pattern may cause performance issues"
        
        return None

    def _execute_with_timeout(self, sql: str):
        """Execute SQL query with timeout protection."""
        from typing import List, Any
        
        result: List[Any] = [None]
        error: List[Any] = [None]
        
        def execute_query():
            try:
                result[0] = self.db.execute_query(sql)
            except Exception as e:
                error[0] = e
        
        # Start query execution in a separate thread
        query_thread = threading.Thread(target=execute_query)
        query_thread.daemon = True
        query_thread.start()
        
        # Wait for completion with timeout
        query_thread.join(timeout=self.timeout_seconds)
        
        if query_thread.is_alive():
            # Query is still running - this is a timeout
            raise TimeoutError(f"Query execution exceeded {self.timeout_seconds} seconds")
        
        if error[0] is not None:
            raise error[0]
        
        return result[0]

    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for exponential backoff with jitter."""
        delay = min(self.base_delay * (2 ** attempt), self.max_delay)
        # Add jitter (random variation between 0 and delay * 0.1)
        jitter = random.uniform(0, delay * 0.1)
        return float(delay + jitter)

    def set_retry_config(self, max_retries: int, timeout_seconds: int):
        """Update retry configuration."""
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds

    def get_execution_stats(self) -> dict:
        """Get execution statistics for monitoring."""
        return {
            "max_retries": self.max_retries,
            "timeout_seconds": self.timeout_seconds,
            "base_delay": self.base_delay,
            "max_delay": self.max_delay
        }
