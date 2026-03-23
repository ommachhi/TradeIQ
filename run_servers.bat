@echo off
REM Run both backend and frontend servers

echo.
echo ========================================
echo   TradeIQ - Stock Market Prediction
echo   Starting Both Servers
echo ========================================
echo.

REM Check if backend and frontend directories exist
if not exist "tradeiq_backend" (
    echo Error: tradeiq_backend directory not found!
    exit /b 1
)

if not exist "tradeiq_frontend" (
    echo Error: tradeiq_frontend directory not found!
    exit /b 1
)

REM Check if virtual environment exists
if not exist ".venv" (
    echo Error: Virtual environment not found!
    echo Please run: python -m venv .venv
    exit /b 1
)

echo Starting Django Backend...
echo Backend will run on: http://localhost:8000
echo.

REM Start backend in a new window
start cmd /k "call .venv\Scripts\activate && cd tradeiq_backend && python manage.py runserver"

REM Wait a bit for backend to start
timeout /t 3 /nobreak

echo Starting React Frontend...
echo Frontend will run on: http://localhost:5173
echo.

REM Start frontend in a new window
start cmd /k "cd tradeiq_frontend && npm run dev"

echo.
echo ========================================
echo   Both servers are starting!
echo   Backend: http://localhost:8000
echo   Frontend: http://localhost:5173
echo ========================================
echo.
echo Press any key to close this window...
pause
