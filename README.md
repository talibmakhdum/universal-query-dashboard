# 🌌 Universal Query Dashboard (v2.0)

**Next-Generation Agentic Analytics & Natural Language Data Intelligence**

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Frontend-Next.js-000000?style=flat-square&logo=next.js)](https://nextjs.org/)
[![Google Gemini](https://img.shields.io/badge/AI-Google%20Gemini-4285F4?style=flat-square&logo=google-gemini)](https://ai.google.dev/)
[![LangGraph](https://img.shields.io/badge/Workflow-LangGraph-FF6F00?style=flat-square&logo=chainlink)](https://langchain.com/langgraph)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)](https://opensource.org/licenses/MIT)

The **Universal Query Dashboard** is an enterprise-grade analytics platform that transforms complex datasets—databases and CSV files—into actionable insights using Natural Language. Unlike simple chatbots, it utilizes a **Multi-Agent Orchestration** system to plan, write, audit, and execute data operations with self-correcting capabilities.

---

## 🌟 Vision: From Querying to Conversing
Traditional BI tools require SQL knowledge or rigid drag-and-drop interfaces. Our system allows you to ask:
- *"Show me the correlation between mileage and price for electric vehicles."*
- *"Based on this CSV, what are the top 5 emerging trends in our sales data?"*

---

## 🚀 Key Modules & Innovations

### 🤖 The Agentic Neural Network (LangGraph)
Our system doesn't just "guess" a query. It passes your request through a sophisticated specialized loop:
- **Planner Agent**: Analyzes the schema and formulates a multi-step logical strategy.
- **SQL Writer**: Generates optimized SQLite queries with metadata awareness.
- **SQL Critic**: A security layer that audits queries for performance bottlenecks and SQL-injection attempts.
- **Executor Agent**: Safely runs queries with an automated retry logic and exponential backoff.
- **Self-Correction Loop**: If a query fails, the Critic feeds the error back to the Writer for an immediate fix.

### 🐍 Advanced CSV "Code Interpreter"
V2.0 introduces a state-of-the-art CSV analysis pipeline. Instead of simple row matching, the AI generates **dynamic Python processing code** to analyze your full dataset. 
- **Mathematical Accuracy**: Performs full aggregations (sums, means, medians) on the entire file.
- **Intelligent Insight**: Generates secondary business interpretations alongside the raw data.
- **Auto-Visualization**: Automatically selects between Bar, Line, Pie, or KPI charts based on data characteristics.

### 💎 Premium Glassmorphism UI
A "visual-first" dashboard experience built for the modern era:
- **Real-time Reasoning**: Watch the AI "think" through a dedicated thought-process sidebar.
- **Live System Health**: Monitor CPU, Memory, and Query success rates in real-time.
- **Dynamic Context**: Seamlessly switch between database querying and CSV analysis modes.

---

## 🛠 Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | Next.js 14 (App Router), TypeScript, Tailwind CSS, Lucide Icons |
| **Backend** | FastAPI, Python 3.14+, Pydantic v2 |
| **AI/LLM** | Google Gemini 2.0 Flash, ChatGoogleGenerativeAI |
| **Orchestration** | LangGraph (Stateful Workflows), LangChain |
| **Data** | SQLite, Pandas (Analysis Core) |
| **Visualization** | Recharts (Responsive UI Components) |

---

## ⚙️ Installation & Setup

### Prerequisites
- **Python**: 3.14+ (Recommended)
- **Node.js**: 18+ (LTS)
- **API Key**: [Google AI Studio](https://aistudio.google.com/) Gemini API Key.

### 1. Backend Configuration
```bash
cd backend
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

python -m pip install -r requirements.txt
```
Create a `.env` file in the `backend/` directory:
```env
GEMINI_API_KEY=your_actual_key_here
```

### 2. Frontend Configuration
```bash
cd frontend
npm install --legacy-peer-deps
```

### 3. Execution
**Window 1 (Backend):**
```bash
cd backend
python app.pynpm 
```

**Window 2 (Frontend):**
```bash
cd frontend
npm run dev
```

---

## 🛡️ Security & Enterprise Integrity
- **Read-Only Enforcement**: Every query is audited by the Critic to block `DROP`, `DELETE`, or `UPDATE` commands.
- **Resource Sandboxing**: Query execution is time-limited to prevent long-running processes from hanging the server.
- **Local Persistence**: Data stays in your local SQLite/CSV environment; only anonymized schemas are sent for AI planning.

---

## 🤝 Contributing
We are building the future of data democratizing. If you have ideas for new agents or visualization patterns, feel free to open a Pull Request.

---

## 📄 License
Distributed under the MIT License. See `LICENSE` for more information.

---
**Transforming raw data into narrative intelligence.**  
Developed by [Talib Makhdum](https://github.com/talibmakhdum)