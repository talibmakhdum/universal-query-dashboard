@echo off
echo ===================================================
echo   Universal Query Dashboard - One Click Setup
echo ===================================================

echo [1/3] Setting up Backend Virtual Environment...
cd backend
python -m venv venv
call .\venv\Scripts\activate
pip install -r requirements.txt
if not exist .env (
    copy .env.example .env
    echo.
    echo ! WARNING: Created .env file from template. 
    echo ! Please add your GEMINI_API_KEY to backend/.env
)
cd ..

echo [2/3] Installing Frontend Dependencies...
cd frontend
npm install --legacy-peer-deps
if not exist .env.local (
    copy .env.example .env.local
)
cd ..

echo [3/3] Finalizing...
echo.
echo Setup Complete!
echo.
echo To start the application:
echo 1. Open a terminal and run: cd backend and python app.py
echo 2. Open another terminal and run: cd frontend and npm run dev
echo.
pause
