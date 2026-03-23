#!/bin/bash

# Run both backend and frontend servers for TradeIQ

echo ""
echo "========================================"
echo "  TradeIQ - Stock Market Prediction"
echo "  Starting Both Servers"
echo "========================================"
echo ""

# Check if backend and frontend directories exist
if [ ! -d "tradeiq_backend" ]; then
    echo "Error: tradeiq_backend directory not found!"
    exit 1
fi

if [ ! -d "tradeiq_frontend" ]; then
    echo "Error: tradeiq_frontend directory not found!"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Error: Virtual environment not found!"
    echo "Please run: python3 -m venv .venv"
    exit 1
fi

# Start backend in background
echo "Starting Django Backend..."
echo "Backend will run on: http://localhost:8000"
echo ""

source .venv/bin/activate
(cd tradeiq_backend && python manage.py runserver) &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 3

# Start frontend in background
echo "Starting React Frontend..."
echo "Frontend will run on: http://localhost:5173"
echo ""

(cd tradeiq_frontend && npm run dev) &
FRONTEND_PID=$!

echo ""
echo "========================================"
echo "  Both servers are running!"
echo "  Backend: http://localhost:8000"
echo "  Frontend: http://localhost:5173"
echo "========================================"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
