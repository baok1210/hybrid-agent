#!/bin/bash
# Stop Hybrid Agent Server

echo "🛑 Stopping Hybrid Agent..."

# Find and kill the server process
PIDS=$(ps aux | grep "python api_server.py" | grep -v grep | awk '{print $2}')

if [ -z "$PIDS" ]; then
    echo "⚠️  Hybrid Agent is not running"
else
    echo "🔪 Killing process(es): $PIDS"
    echo $PIDS | xargs kill -9 2>/dev/null || true
    echo "✅ Hybrid Agent stopped"
fi

# Also kill uvicorn
UVICORN_PIDS=$(ps aux | grep "uvicorn" | grep -v grep | awk '{print $2}')
if [ ! -z "$UVICORN_PIDS" ]; then
    echo "🔪 Killing uvicorn: $UVICORN_PIDS"
    echo $UVICORN_PIDS | xargs kill -9 2>/dev/null || true
fi
