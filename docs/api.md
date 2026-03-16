# Universal Query Dashboard API Documentation

## Overview

The Universal Query Dashboard provides a RESTful API for natural language query processing with multi-agent architecture. This API enables users to upload datasets, process natural language questions, and receive structured results with visualizations.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication. In production environments, consider implementing API key authentication or OAuth2.

## Response Format

All API responses follow a consistent format:

```json
{
  "success": boolean,
  "data": object | array | null,
  "error": string | null,
  "timestamp": string,
  "execution_time_ms": number
}
```

## Endpoints

### System Information

#### GET /health
Health check endpoint to verify system status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-03-16 23:45:30",
  "version": "2.0.0",
  "uptime": "system_running"
}
```

#### GET /system-info
Get detailed system information and capabilities.

**Response:**
```json
{
  "success": true,
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
      "self_correcting": true,
      "context_aware": true,
      "real_time_processing": true,
      "error_handling": true
    }
  }
}
```

### Data Management

#### GET /tables
Retrieve list of available database tables.

**Response:**
```json
{
  "success": true,
  "tables": ["vehicles", "customers", "orders"],
  "count": 3
}
```

#### POST /upload-csv
Upload a CSV file for analysis.

**Request:**
- Content-Type: multipart/form-data
- File field: `file` (CSV file, max 50MB)

**Response:**
```json
{
  "success": true,
  "file_path": "uploads/uuid_filename.csv",
  "filename": "data.csv",
  "size": "24.50KB",
  "message": "Successfully uploaded data.csv"
}
```

**Error Responses:**
```json
{
  "success": false,
  "error": "Only CSV files are supported for upload",
  "error_type": "VALIDATION_ERROR",
  "field": "file",
  "value": "data.txt",
  "suggestion": "Ensure all required fields are filled with valid data."
}
```

### Query Processing

#### POST /query
Process a natural language query and return results.

**Request Body:**
```json
{
  "question": "What are the top 5 best-selling products?",
  "table_name": "products",
  "session_id": "user_session_123",
  "is_csv": false,
  "csv_path": null
}
```

**Request Parameters:**
- `question` (string, required): The natural language query
- `table_name` (string, required for database queries): Target database table
- `session_id` (string, optional): Session identifier for conversation memory
- `is_csv` (boolean, optional): Whether to use CSV analysis pipeline
- `csv_path` (string, optional): Path to CSV file (required if is_csv is true)

**Response:**
```json
{
  "success": true,
  "data": [
    {"product_name": "Product A", "sales": 1500},
    {"product_name": "Product B", "sales": 1200},
    {"product_name": "Product C", "sales": 900}
  ],
  "chartType": "bar",
  "insight": "Product A has the highest sales with 1500 units sold.",
  "sql": "SELECT product_name, SUM(quantity) as sales FROM orders GROUP BY product_name ORDER BY sales DESC LIMIT 5",
  "sqlType": "success",
  "execution_time_ms": 145.2,
  "timestamp": "2024-03-16 23:45:30",
  "thought_process": [
    "Planner: Analyzing your question and selecting relevant tables...",
    "SQL Writer: Generating optimized SQL query...",
    "SQL Critic: Performing comprehensive security and performance validation...",
    "Executor: Running query on database...",
    "Executor: Successfully retrieved 3 rows."
  ]
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Security violation detected. This operation is not permitted.",
  "error_type": "SECURITY_ERROR",
  "violation_type": "SQL_INJECTION",
  "suggestion": "Ensure your query follows security guidelines.",
  "execution_time_ms": 23.1,
  "timestamp": "2024-03-16 23:45:30"
}
```

### Session Management

#### POST /clear-session
Clear conversation history for a specific session.

**Request Body:**
```json
{
  "session_id": "user_session_123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Session user_session_123 cleared successfully",
  "session_id": "user_session_123"
}
```

#### GET /session-stats/{session_id}
Get statistics for a specific session.

**Response:**
```json
{
  "success": true,
  "session_id": "user_session_123",
  "summary": {
    "session_id": "user_session_123",
    "total_queries": 15,
    "last_activity": "2024-03-16 23:45:30",
    "common_topics": ["sales", "inventory", "performance"],
    "query_types": {
      "sales": 8,
      "inventory": 4,
      "performance": 3
    },
    "session_duration": "2:15:30"
  }
}
```

### Monitoring and Metrics

#### GET /metrics
Get comprehensive performance statistics.

**Response:**
```json
{
  "query_stats": {
    "total_queries": 1250,
    "success_rate": 96.8,
    "avg_execution_time": 245.3,
    "avg_agent_steps": 3.2,
    "avg_result_count": 45.7,
    "error_breakdown": {
      "TIMEOUT": 15,
      "VALIDATION": 8,
      "DATABASE": 5
    },
    "performance_by_table": {
      "vehicles": {
        "query_count": 800,
        "avg_execution_time": 180.5,
        "min_execution_time": 45.2,
        "max_execution_time": 1200.0
      }
    }
  },
  "system_stats": {
    "avg_cpu": 45.2,
    "avg_memory": 67.8,
    "avg_disk": 23.4,
    "max_active_connections": 15,
    "avg_queries_per_minute": 8.5,
    "current_load": {
      "cpu": 32.1,
      "memory": 58.7,
      "memory_used_mb": 2048.5,
      "disk": 21.3,
      "active_connections": 8,
      "queries_per_minute": 6.2
    }
  },
  "agent_performance": {
    "avg_steps_per_query": 3.1,
    "steps_distribution": {
      "2": 120,
      "3": 850,
      "4": 200,
      "5": 80
    },
    "performance_by_steps": {
      "3": {
        "query_count": 850,
        "avg_execution_time": 210.5,
        "success_rate": 97.6
      }
    },
    "efficiency_trends": [
      {
        "hour": 9,
        "total_queries": 45,
        "avg_steps": 3.2,
        "step_breakdown": {"2": 10, "3": 25, "4": 10}
      }
    ]
  },
  "health": {
    "status": "healthy",
    "timestamp": "2024-03-16T23:45:30",
    "system_health": {
      "cpu": "healthy",
      "memory": "healthy", 
      "disk": "healthy",
      "queries": "healthy"
    },
    "recommendations": ["System is running optimally."]
  }
}
```

#### GET /health/status
Get detailed system health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-03-16T23:45:30",
  "system_health": {
    "cpu": "healthy",
    "memory": "healthy",
    "disk": "healthy", 
    "queries": "healthy"
  },
  "metrics": {
    "system": {
      "avg_cpu": 45.2,
      "avg_memory": 67.8,
      "avg_disk": 23.4,
      "max_active_connections": 15,
      "avg_queries_per_minute": 8.5,
      "current_load": {
        "cpu": 32.1,
        "memory": 58.7,
        "memory_used_mb": 2048.5,
        "disk": 21.3,
        "active_connections": 8,
        "queries_per_minute": 6.2
      }
    },
    "queries": {
      "total_queries": 1250,
      "success_rate": 96.8,
      "avg_execution_time": 245.3,
      "avg_agent_steps": 3.2,
      "avg_result_count": 45.7,
      "error_breakdown": {
        "TIMEOUT": 15,
        "VALIDATION": 8,
        "DATABASE": 5
      }
    }
  },
  "recommendations": ["System is running optimally."]
}
```

## Error Handling

The API provides detailed error responses with the following structure:

```json
{
  "success": false,
  "error": "User-friendly error message",
  "error_type": "ERROR_CATEGORY",
  "details": {
    "technical_details": "Detailed error information"
  },
  "suggestion": "Suggested action to resolve the error",
  "execution_time_ms": 12.5,
  "timestamp": "2024-03-16 23:45:30"
}
```

### Error Types

- `VALIDATION_ERROR`: Input validation failed
- `DATABASE_ERROR`: Database connection or query error
- `SECURITY_ERROR`: Security violation detected
- `AGENT_ERROR`: Agent processing error
- `QUERY_ERROR`: General query processing error
- `INTERNAL_ERROR`: Unexpected server error

### HTTP Status Codes

- `200`: Success
- `400`: Bad Request (validation errors)
- `404`: Not Found
- `500`: Internal Server Error
- `503`: Service Unavailable

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **Default Limit**: 60 requests per minute per IP
- **Burst Limit**: 10 requests per second
- **CSV Upload Limit**: 50MB per file

## CORS

The API supports CORS for cross-origin requests:

```http
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
```

## Performance Headers

All responses include performance metrics:

```http
X-Process-Time: 0.123
X-Query-Time: 45.67
X-Agent-Steps: 3
```

## SDK Examples

### Python
```python
import requests

# Process a query
response = requests.post('http://localhost:8000/query', json={
    'question': 'What are the top products by sales?',
    'table_name': 'products',
    'session_id': 'user_123'
})

if response.json()['success']:
    data = response.json()['data']
    chart_type = response.json()['chartType']
    sql = response.json()['sql']
```

### JavaScript
```javascript
// Process a query
const response = await fetch('http://localhost:8000/query', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    question: 'What are the top products by sales?',
    table_name: 'products',
    session_id: 'user_123'
  })
});

const result = await response.json();
if (result.success) {
  console.log(result.data);
  console.log(result.chartType);
  console.log(result.sql);
}
```

## Webhook Support

The API supports webhooks for real-time notifications (planned feature):

- Query completion notifications
- System health alerts
- Performance threshold breaches

## Versioning

The API follows semantic versioning:

- **Current Version**: v2.0.0
- **Backward Compatibility**: Maintained for v1.x endpoints
- **Deprecation Policy**: 6 months notice for deprecated endpoints

## Security

### Best Practices

1. **Input Validation**: All inputs are validated server-side
2. **SQL Injection Prevention**: Multi-layer protection against SQL injection
3. **File Upload Security**: File type and size validation
4. **Error Information**: Sensitive information is sanitized in error messages
5. **Rate Limiting**: Protection against abuse and DoS attacks

### Security Headers

The API includes security headers:

```http
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

## Monitoring

### Health Checks

Use the `/health` endpoint for load balancer health checks:

```bash
curl -f http://localhost:8000/health || exit 1
```

### Metrics Collection

The API provides metrics for monitoring:

- Query performance metrics
- System resource usage
- Agent performance statistics
- Error rate tracking

### Logging

The API logs all requests for debugging and monitoring:

- Request/response logging
- Performance metrics
- Error details
- Security events

## Troubleshooting

### Common Issues

1. **High Latency**: Check system resources and query complexity
2. **Query Failures**: Review error messages and input validation
3. **File Upload Issues**: Verify file format and size limits
4. **Session Problems**: Check session ID format and expiration

### Debug Mode

Enable debug mode for detailed logging:

```bash
export DEBUG=true
python app.py
```

### Support

For API support:
- Check the error messages and suggestions
- Review the system health status
- Monitor performance metrics
- Contact support with error details and timestamps