#!/bin/bash

# Core DNA RAG Chatbot Startup Script
# Run this script to start both backend and frontend servers

echo "🚀 Starting Core DNA RAG Chatbot..."

# Check if we're in the right directory
if [ ! -f "PROJECT_STATUS.md" ]; then
    echo "❌ Please run this script from the /Users/therese/Desktop/coredna directory"
    exit 1
fi

# Start backend server in background
echo "📡 Starting backend server..."
cd chatbot-backend
source venv/bin/activate
python production_server.py &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Start frontend server
echo "🌐 Starting frontend server..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Servers started successfully!"
echo ""
echo "🔗 Access your chatbot:"
echo "   Frontend: http://localhost:3000"
echo "   API Docs: http://localhost:8000/docs"
echo "   Health:   http://localhost:8000/health"
echo ""
echo "📝 Backend PID: $BACKEND_PID"
echo "📝 Frontend PID: $FRONTEND_PID"
echo ""
echo "⚠️  To stop servers: Press Ctrl+C or run 'pkill -f production_server' and 'pkill -f next'"
echo ""

# Wait for user to press Ctrl+C
trap 'echo ""; echo "🛑 Stopping servers..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit' INT

# Keep script running
wait