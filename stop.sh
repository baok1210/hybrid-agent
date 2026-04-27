#!/usr/bin/env bash
echo "🛑 Stopping Hybrid Agent AI Provider..."

# Find PID of uvicorn process running api_server
PID=$(pgrep -f "uvicorn.*api_server")

if [ -z "$PID" ]; then
    echo "⚠️  Server is not running."
else
    echo "🔪 Killing process $PID..."
    kill $PID
    sleep 2
    # Double check and force kill if necessary
    if pgrep -f "uvicorn.*api_server" > /dev/null; then
        echo "⚠️  Server didn't stop, forcing kill..."
        pkill -9 -f "uvicorn.*api_server"
    fi
    echo "✅ Server stopped."
fi

# Clean up PID file if exists
if [ -f ".server.pid" ]; then
    rm .server.pid
fi
