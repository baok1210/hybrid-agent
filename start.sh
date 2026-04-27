#!/bin/bash
# Start Hybrid Agent v3.0 with auto-launch Chrome

set -e

cd "$(dirname "$0")"

# Create logs directory
mkdir -p logs

echo "🚀 Starting Hybrid Agent v3.0..."

# Activate venv
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ Virtual environment not found. Run ./install.sh first"
    exit 1
fi

# Check if Chrome is already running with CDP
if lsof -i:9222 > /dev/null 2>&1; then
    echo "✅ Chrome already running on port 9222"
else
    echo "🌐 Launching Chrome with CDP..."
    python3 browser_launcher.py &
    CHROME_PID=$!
    echo $CHROME_PID > .chrome.pid
    sleep 5
fi

# Start API server
echo "🔧 Starting API server on port 8001..."
uvicorn api_server:app \
    --host 0.0.0.0 \
    --port 8001 \
    --log-level info \
    > logs/server.log 2>&1 &

SERVER_PID=$!
echo $SERVER_PID > .server.pid

echo "✅ Hybrid Agent started!"
echo "📍 API: http://localhost:8001"
echo "📍 Health: http://localhost:8001/health"
echo "📍 Models: http://localhost:8001/v1/models"
echo ""
echo "💡 Available models:"
echo "   - chatgpt (ChatGPT latest)"
echo "   - gemini (Google Gemini latest)"
echo "   - claude (Claude latest)"
echo ""
echo "🔧 Usage in Clawx/Hermes:"
echo "   Base URL: http://localhost:8001/v1"
echo "   API Key: hybrid-free-key-2026"
echo "   Model: chatgpt | gemini | claude"
echo ""
echo "🛑 Stop: ./stop.sh"
