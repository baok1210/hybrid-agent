#!/bin/bash
# Script khởi động Hybrid Agent API Server

set -e

echo "🚀 Khởi động Hybrid Agent API Server..."

# Kiểm tra Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 không được cài đặt"
    exit 1
fi

# Cài đặt dependencies
echo "📦 Cài đặt dependencies..."
pip3 install -r requirements.txt

# Khởi động server
echo "🌐 Server đang chạy trên http://localhost:8001"
echo "📚 API docs: http://localhost:8001/docs"
echo ""

python3 api_server.py --host 0.0.0.0 --port 8001
