# Universal Query Dashboard

[![Next.js](https://img.shields.io/badge/Next.js-14-black?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

**Talk to your data in plain English.**  
Upload any CSV → ask natural questions → get instant insights, beautiful charts, and smart answers — powered by Google Gemini.

No SQL. No coding. Just curiosity.

## ✨ Key Features

- Natural language questions (“What’s the top product by revenue last quarter?”)
- Auto-generated interactive charts (bar, line, pie, area, KPI cards)
- Follow-up questions with full conversation memory
- Smart query suggestions based on your dataset
- Export charts (PNG) and data (CSV)
- Secure local processing — your data stays private
- Fast, responsive UI built for modern browsers

## 🛠 Tech Stack

- **Frontend**: Next.js 14 (App Router) · TypeScript · Tailwind CSS · Recharts  
- **Backend**: FastAPI · Python 3.10+ · SQLite  
- **AI**: Google Gemini Pro (natural language → SQL + insights)  
- **Validation**: Zod · Pydantic  

## 🚀 Quick Start

### Prerequisites
- Node.js ≥ 18
- Python ≥ 3.10
- [Google Gemini API Key](https://ai.google.dev/)

### 1. Clone & Install
```bash
git clone https://github.com/talibmakhdum/universal-query-dashboard.git
cd universal-query-dashboard