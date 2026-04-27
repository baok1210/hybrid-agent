#!/usr/bin/env bash
set -e

echo "🚀 Starting Hybrid Agent AI Provider..."

# Check if already running
if pgrep -f "uvicorn.*api_server" > /dev/null; then
    echo "⚠️  Server is already running. Stopping first..."
    ./stop.sh
    sleep 2
fi

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ Virtual environment not found. Run ./install.sh first."
    exit 1
fi

# Check dependencies
if ! python -c "import fastapi" &> /dev/null; then
    echo "❌ FastAPI not installed. Run ./install.sh first."
    exit 1
fi

# Create logs directory
mkdir -p logs

# Load configuration
if [ -f "config.yaml" ]; then
    PORT=$(grep -E "^\s*port:\s*" config.yaml | awk '{print $2}' | head -1)
    if [ -z "$PORT" ]; then
        PORT=8001
    fi
else
    PORT=8001
fi

# Start server in background
echo "🌐 Starting API server on port $PORT..."
PYTHONPATH=/home/bun/hybrid-agent/hybrid-agent:$PYTHONPATH nohup python -m uvicorn hybrid-agent.api_server:app \
    --host 0.0.0.0 \
    --port $PORT \
    --reload \
    --log-level info \
    > logs/server.log 2>&1 &

SERVER_PID=$!
echo $SERVER_PID > .server.pid

# Wait for server to start
echo "⏳ Waiting for server to start..."
sleep 3

# Check if server is running
if curl -s http://localhost:$PORT/health > /dev/null 2>&1; then
    echo "✅ Server started successfully!"
    echo "📊 Health check: http://localhost:$PORT/health"
    echo "🔗 API endpoint: http://localhost:$PORT/v1/chat/completions"
    echo "📝 Logs: tail -f logs/server.log"
    echo ""
    echo "To stop server: ./stop.sh"
else
    echo "❌ Server failed to start. Check logs:"
    tail -20 logs/server.log
    exit 1
fi

# Show test command
echo ""
echo "🧪 Test with:"
echo "curl -X POST http://localhost:$PORT/v1/chat/completions \\"
echo "  -H \"Authorization: Bearer hybrid-free-key-2026\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"messages\":[{\"role\":\"user\",\"content\":\"Hello\"}]}'"