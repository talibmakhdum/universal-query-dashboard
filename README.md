# Universal Query Dashboard

[![Next.js](https://img.shields.io/badge/Next.js-14-black?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![LangGraph](https://img.shields.io/badge/LangGraph-000000?style=for-the-badge&logo=langchain)](https://langchain.com/langgraph)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

**Enterprise-Grade Agentic Analytics System**  
Transform natural language questions into intelligent SQL queries with self-correcting multi-agent architecture, real-time performance monitoring, and production-ready error handling.

## 🚀 What's New in v2.0

### 🤖 **Agentic Architecture**
- **Planner Agent**: Intelligently analyzes questions and selects optimal data sources
- **SQL Writer Agent**: Generates optimized, metadata-aware SQL queries
- **SQL Critic Agent**: Validates queries for security, performance, and correctness
- **Executor Agent**: Handles query execution with retry logic and timeout management
- **Self-Correcting Loop**: Automatic query regeneration on validation failures

### 🛡️ **Enterprise Security**
- Multi-layer SQL injection prevention
- Forbidden operation detection (DROP, DELETE, UPDATE, etc.)
- Performance anti-pattern validation
- Schema compliance checking
- Input sanitization and validation

### 📊 **Advanced Analytics**
- Context-aware conversation memory with summarization
- Real-time performance monitoring and metrics
- Agent performance tracking and optimization
- System health monitoring with recommendations
- Query execution time tracking and optimization

### 🎨 **Enhanced UI/UX**
- Glassmorphism design with smooth animations
- Real-time agent reasoning visualization
- Enhanced SQL query display with status indicators
- Performance metrics and system status dashboard
- Improved error handling with user-friendly messages

## ✨ Key Features

### Core Capabilities
- **Natural Language Processing**: Ask questions in plain English
- **Multi-Agent SQL Generation**: Self-correcting query generation pipeline
- **Auto Chart Generation**: Intelligent chart type detection and rendering
- **Conversation Memory**: Context-aware follow-up question handling
- **CSV Analysis Pipeline**: Upload and analyze any CSV dataset
- **Real-time Performance Monitoring**: Track system health and agent efficiency

### Enterprise Features
- **Security Validation**: Comprehensive SQL injection and security checks
- **Performance Optimization**: Query optimization suggestions and monitoring
- **Error Handling**: Production-grade error handling with detailed logging
- **System Monitoring**: CPU, memory, disk usage, and query rate tracking
- **Session Management**: Advanced session handling with cleanup and summarization

## 🛠 Tech Stack

### Backend Architecture
- **Framework**: FastAPI with comprehensive middleware
- **AI Orchestration**: LangGraph for multi-agent workflows
- **Database**: SQLite with connection pooling and optimization
- **AI Models**: Google Gemini Pro for natural language processing
- **Monitoring**: Custom metrics collection with psutil integration
- **Error Handling**: Centralized error handling with structured logging

### Frontend Architecture
- **Framework**: Next.js 14 with App Router
- **Styling**: Tailwind CSS with custom glassmorphism design
- **Charts**: Recharts for interactive data visualization
- **State Management**: Context API with optimized state updates
- **UI Components**: Custom components with enhanced animations

### Agent System
- **Planner Agent**: Question analysis and strategy planning
- **SQL Writer Agent**: Optimized SQL generation with metadata integration
- **SQL Critic Agent**: Security and performance validation
- **Executor Agent**: Robust query execution with retry logic
- **Memory Manager**: Context-aware conversation history

## 🚀 Quick Start

### Prerequisites
- Node.js ≥ 18
- Python ≥ 3.10
- [Google Gemini API Key](https://ai.google.dev/)
- pip packages from `requirements.txt`

### 1. Clone & Install
```bash
git clone https://github.com/talibmakhdum/universal-query-dashboard.git
cd universal-query-dashboard

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies
cd frontend
npm install
```

### 2. Environment Setup
```bash
# Create .env file in backend directory
echo "GOOGLE_API_KEY=your_gemini_api_key_here" > backend/.env
```

### 3. Initialize Database
```bash
# Run the database initialization script
cd backend
python init_db.py
```

### 4. Start Services
```bash
# Start backend (in backend directory)
python app.py

# Start frontend (in frontend directory)
npm run dev
```

### 5. Access Dashboard
Open your browser and navigate to `http://localhost:3000`

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway    │    │   Agent Graph   │
│   (Next.js)     │◄──►│   (FastAPI)      │◄──►│   (LangGraph)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Charts        │    │   Error Handler  │    │   Memory Mgmt   │
│   (Recharts)    │    │   (Centralized)  │    │   (Session)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Database      │    │   Monitoring     │    │   Validation    │
│   (SQLite)      │    │   (Performance)  │    │   (Security)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Agent Workflow
1. **User Input** → Question processing and validation
2. **Planner Agent** → Analyzes question, selects data sources, creates strategy
3. **SQL Writer Agent** → Generates optimized SQL with metadata integration
4. **SQL Critic Agent** → Validates for security, performance, and correctness
5. **Executor Agent** → Executes query with retry logic and error handling
6. **Result Processing** → Chart generation and insight extraction
7. **Memory Update** → Conversation history and context management

## 📊 Performance Monitoring

The system includes comprehensive performance monitoring:

### Query Metrics
- Execution time tracking
- Agent step efficiency
- Success rate monitoring
- Error type analysis
- Performance by table/dataset

### System Metrics
- CPU and memory usage
- Disk space monitoring
- Active connection tracking
- Query rate limiting
- System health status

### Agent Performance
- Steps distribution analysis
- Efficiency trends over time
- Performance by agent type
- Optimization recommendations

## 🔧 Configuration

### Environment Variables
```bash
# Required
GOOGLE_API_KEY=your_gemini_api_key

# Optional
DATABASE_PATH=data.db
UPLOAD_DIR=uploads
MAX_FILE_SIZE=52428800  # 50MB
QUERY_TIMEOUT=30         # seconds
MAX_RETRIES=3
```

### Agent Configuration
```python
# Backend configuration
EXECUTOR_CONFIG = {
    'max_retries': 3,
    'timeout_seconds': 30,
    'base_delay': 1.0,
    'max_delay': 10.0
}

MEMORY_CONFIG = {
    'max_history_length': 15,
    'context_window_hours': 24
}
```

## 🚨 Security Features

### SQL Injection Prevention
- Pattern-based injection detection
- Parameterized query validation
- Forbidden operation blocking
- Input sanitization

### Performance Security
- Query timeout enforcement
- Resource usage monitoring
- Rate limiting implementation
- Memory leak prevention

### Data Security
- Local processing only
- No external data transmission
- Secure session management
- Encrypted error logging

## 📈 API Endpoints

### Core Endpoints
- `GET /health` - System health check
- `GET /system-info` - System capabilities and features
- `GET /tables` - Available database tables
- `POST /query` - Process natural language query
- `POST /upload-csv` - Upload CSV for analysis

### Management Endpoints
- `POST /clear-session` - Clear conversation history
- `GET /session-stats/{session_id}` - Session performance metrics
- `GET /metrics` - System performance data

### Monitoring Endpoints
- `GET /health/status` - Detailed health status
- `GET /metrics/queries` - Query performance statistics
- `GET /metrics/system` - System resource metrics
- `GET /metrics/agents` - Agent performance data

## 🎨 UI Components

### Enhanced Dashboard
- **Glassmorphism Design**: Modern frosted glass aesthetic
- **Real-time Updates**: Live performance metrics and system status
- **Agent Visualization**: Step-by-step reasoning display
- **Error Handling**: User-friendly error messages with suggestions

### Chart Components
- **Auto Detection**: Intelligent chart type selection
- **Interactive**: Hover effects and tooltips
- **Responsive**: Adapts to different screen sizes
- **Export**: PNG chart export functionality

### Chat Interface
- **Enhanced Messages**: SQL query display with syntax highlighting
- **Performance Metrics**: Execution time and result count
- **Error Visualization**: Clear error status and suggestions
- **Loading States**: Smooth loading animations

## 🧪 Testing

### Unit Tests
```bash
# Backend tests
cd backend
python -m pytest tests/

# Frontend tests
cd frontend
npm test
```

### Integration Tests
```bash
# Full system test
python tests/integration_test.py
```

### Performance Tests
```bash
# Load testing
python tests/performance_test.py
```

## 📚 Documentation

- [API Documentation](docs/api.md)
- [Agent Architecture](docs/agents.md)
- [Performance Monitoring](docs/monitoring.md)
- [Security Guidelines](docs/security.md)
- [Deployment Guide](docs/deployment.md)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **LangChain/LangGraph** - For the powerful agent orchestration framework
- **Google Gemini** - For advanced natural language processing capabilities
- **FastAPI** - For the robust backend framework
- **Next.js** - For the modern frontend framework
- **Recharts** - For beautiful data visualization

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Join our Discord community
- Email us at support@universalquery.com

---

**Transform your data analysis workflow with the power of AI-driven natural language queries.**
