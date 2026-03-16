"""
Centralized error handling for the Universal Query Dashboard.
Provides consistent error responses and logging across all components.
"""

import logging
import traceback
from typing import Dict, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class QueryError(Exception):
    """Base exception for query-related errors."""
    def __init__(self, message: str, error_type: str = "QUERY_ERROR", details: Optional[Dict] = None):
        self.message = message
        self.error_type = error_type
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(Exception):
    """Exception for validation errors."""
    def __init__(self, message: str, field: str = None, value: Any = None):
        self.message = message
        self.field = field
        self.value = value
        super().__init__(self.message)


class DatabaseError(Exception):
    """Exception for database-related errors."""
    def __init__(self, message: str, sql_state: str = None, error_code: int = None):
        self.message = message
        self.sql_state = sql_state
        self.error_code = error_code
        super().__init__(self.message)


class SecurityError(Exception):
    """Exception for security violations."""
    def __init__(self, message: str, violation_type: str = None):
        self.message = message
        self.violation_type = violation_type
        super().__init__(self.message)


class AgentError(Exception):
    """Exception for agent-related errors."""
    def __init__(self, message: str, agent_name: str = None, step: str = None):
        self.message = message
        self.agent_name = agent_name
        self.step = step
        super().__init__(self.message)


class ErrorHandler:
    """Centralized error handler for the application."""
    
    @staticmethod
    def handle_error(
        error: Exception, 
        context: str = None, 
        user_friendly: bool = True
    ) -> Dict[str, Any]:
        """
        Handle an error and return a structured response.
        
        Args:
            error: The exception to handle
            context: Additional context about where the error occurred
            user_friendly: Whether to return user-friendly messages
        
        Returns:
            Dict containing error information
        """
        # Log the error with full details
        error_details = ErrorHandler._extract_error_details(error, context)
        logger.error(f"Error occurred: {error_details}")
        
        # Return structured error response
        return ErrorHandler._format_error_response(error, error_details, user_friendly)
    
    @staticmethod
    def _extract_error_details(error: Exception, context: str = None) -> Dict[str, Any]:
        """Extract detailed information about an error."""
        return {
            "timestamp": datetime.now().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "traceback": traceback.format_exc(),
            "details": getattr(error, 'details', {}),
            "agent_name": getattr(error, 'agent_name', None),
            "step": getattr(error, 'step', None),
            "field": getattr(error, 'field', None),
            "value": getattr(error, 'value', None),
            "sql_state": getattr(error, 'sql_state', None),
            "error_code": getattr(error, 'error_code', None),
            "violation_type": getattr(error, 'violation_type', None)
        }
    
    @staticmethod
    def _format_error_response(error: Exception, error_details: Dict, user_friendly: bool) -> Dict[str, Any]:
        """Format error response for API return."""
        if isinstance(error, QueryError):
            return ErrorHandler._format_query_error(error, user_friendly)
        elif isinstance(error, ValidationError):
            return ErrorHandler._format_validation_error(error, user_friendly)
        elif isinstance(error, DatabaseError):
            return ErrorHandler._format_database_error(error, user_friendly)
        elif isinstance(error, SecurityError):
            return ErrorHandler._format_security_error(error, user_friendly)
        elif isinstance(error, AgentError):
            return ErrorHandler._format_agent_error(error, user_friendly)
        else:
            return ErrorHandler._format_generic_error(error, error_details, user_friendly)
    
    @staticmethod
    def _format_query_error(error: QueryError, user_friendly: bool) -> Dict[str, Any]:
        """Format query error response."""
        if user_friendly:
            message = "I encountered an issue while processing your query. Please try rephrasing your question or contact support if the problem persists."
        else:
            message = error.message
        
        return {
            "success": False,
            "error": message,
            "error_type": "QUERY_ERROR",
            "details": error.details if not user_friendly else None,
            "suggestion": "Try simplifying your query or check the available data columns."
        }
    
    @staticmethod
    def _format_validation_error(error: ValidationError, user_friendly: bool) -> Dict[str, Any]:
        """Format validation error response."""
        if user_friendly:
            message = f"Invalid input provided. Please check your input and try again."
        else:
            message = error.message
        
        return {
            "success": False,
            "error": message,
            "error_type": "VALIDATION_ERROR",
            "field": error.field,
            "value": error.value if not user_friendly else None,
            "suggestion": "Ensure all required fields are filled with valid data."
        }
    
    @staticmethod
    def _format_database_error(error: DatabaseError, user_friendly: bool) -> Dict[str, Any]:
        """Format database error response."""
        if user_friendly:
            message = "Database connection issue. Please try again in a moment."
        else:
            message = error.message
        
        return {
            "success": False,
            "error": message,
            "error_type": "DATABASE_ERROR",
            "sql_state": error.sql_state if not user_friendly else None,
            "error_code": error.error_code if not user_friendly else None,
            "suggestion": "Check your database connection and try again."
        }
    
    @staticmethod
    def _format_security_error(error: SecurityError, user_friendly: bool) -> Dict[str, Any]:
        """Format security error response."""
        if user_friendly:
            message = "Security violation detected. This operation is not permitted."
        else:
            message = error.message
        
        return {
            "success": False,
            "error": message,
            "error_type": "SECURITY_ERROR",
            "violation_type": error.violation_type if not user_friendly else None,
            "suggestion": "Ensure your query follows security guidelines."
        }
    
    @staticmethod
    def _format_agent_error(error: AgentError, user_friendly: bool) -> Dict[str, Any]:
        """Format agent error response."""
        if user_friendly:
            message = "Agent processing error. Please try your query again."
        else:
            message = error.message
        
        return {
            "success": False,
            "error": message,
            "error_type": "AGENT_ERROR",
            "agent_name": error.agent_name,
            "step": error.step if not user_friendly else None,
            "suggestion": "Try simplifying your query or contact support."
        }
    
    @staticmethod
    def _format_generic_error(error: Exception, error_details: Dict, user_friendly: bool) -> Dict[str, Any]:
        """Format generic error response."""
        if user_friendly:
            message = "An unexpected error occurred. Please try again or contact support."
        else:
            message = f"{type(error).__name__}: {str(error)}"
        
        return {
            "success": False,
            "error": message,
            "error_type": "INTERNAL_ERROR",
            "details": error_details if not user_friendly else None,
            "suggestion": "Please try again or contact support with the error details."
        }
    
    @staticmethod
    def log_performance_metric(operation: str, duration: float, success: bool, details: Dict = None):
        """Log performance metrics for monitoring."""
        metric = {
            "operation": operation,
            "duration_ms": round(duration * 1000, 2),
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        
        if success:
            logger.info(f"Performance Metric: {metric}")
        else:
            logger.warning(f"Performance Metric (Failed): {metric}")
    
    @staticmethod
    def sanitize_error_message(message: str) -> str:
        """Sanitize error messages for user display."""
        # Remove sensitive information
        sensitive_patterns = [
            r'password\s*=\s*[^&\s]+',
            r'api[_-]?key\s*=\s*[^&\s]+',
            r'token\s*=\s*[^&\s]+',
            r'host\s*=\s*[^&\s]+',
            r'database\s*=\s*[^&\s]+'
        ]
        
        import re
        for pattern in sensitive_patterns:
            message = re.sub(pattern, '[REDACTED]', message, flags=re.IGNORECASE)
        
        return message


# Convenience functions for common error scenarios
def handle_query_error(message: str, details: Dict = None) -> Dict[str, Any]:
    """Handle a query error."""
    error = QueryError(message, details=details)
    return ErrorHandler.handle_error(error, "query_processing")


def handle_validation_error(message: str, field: str = None, value: Any = None) -> Dict[str, Any]:
    """Handle a validation error."""
    error = ValidationError(message, field, value)
    return ErrorHandler.handle_error(error, "input_validation")


def handle_database_error(message: str, sql_state: str = None, error_code: int = None) -> Dict[str, Any]:
    """Handle a database error."""
    error = DatabaseError(message, sql_state, error_code)
    return ErrorHandler.handle_error(error, "database_operation")


def handle_security_error(message: str, violation_type: str = None) -> Dict[str, Any]:
    """Handle a security error."""
    error = SecurityError(message, violation_type)
    return ErrorHandler.handle_error(error, "security_check", user_friendly=False)


def handle_agent_error(message: str, agent_name: str = None, step: str = None) -> Dict[str, Any]:
    """Handle an agent error."""
    error = AgentError(message, agent_name, step)
    return ErrorHandler.handle_error(error, "agent_execution")