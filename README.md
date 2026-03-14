# Universal Query Dashboard

A powerful natural language to interactive dashboard system that works with any uploaded CSV dataset. Transform your data into insights with simple English questions.

## Features

- **Natural Language Queries**: Ask questions in plain English about your data
- **Interactive Visualizations**: Automatic chart generation (bar, line, pie, KPI cards)
- **Conversation Memory**: Follow-up questions with context awareness
- **Dynamic Suggestions**: Smart query suggestions based on your data schema
- **Export Functionality**: Export charts as PNG images
- **Secure Processing**: Read-only database access with SQL injection prevention

## Tech Stack

- **Frontend**: Next.js 14, TypeScript, Tailwind CSS, Recharts
- **Backend**: FastAPI, Python, SQLite
- **AI Integration**: Google Gemini Pro for NL-to-SQL and insights
- **Visualization**: Recharts for interactive dashboards

## Setup Instructions

### Prerequisites
- Node.js 18+
- Python 3.8+
- Google Gemini API Key

### Frontend Setup
1. Navigate to the frontend directory: `cd frontend`
2. Install dependencies: `npm install`
3. Create `.env.local` with: