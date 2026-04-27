#!/usr/bin/env bash
set -e

echo "🚀 Installing Hybrid Agent AI Provider..."

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.8+"
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
echo "✅ Python $PYTHON_VERSION detected"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p data
mkdir -p backups

# Initialize database
echo "🗄️  Initializing database..."
python3 -c "
import sqlite3
import os
db_path = os.path.expanduser('~/.hybrid_agent/state.db')
os.makedirs(os.path.dirname(db_path), exist_ok=True)
conn = sqlite3.connect(db_path)
conn.execute('''
    CREATE TABLE IF NOT EXISTS sessions (
        id TEXT PRIMARY KEY,
        created_at TEXT,
        user_request TEXT,
        status TEXT
    )
''')
conn.execute('''
    CREATE TABLE IF NOT EXISTS steps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        step_num INTEGER,
        thought TEXT,
        actions TEXT,
        results TEXT,
        timestamp TEXT
    )
''')
conn.execute('''
    CREATE TABLE IF NOT EXISTS metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        endpoint TEXT,
        duration_ms REAL,
        status_code INTEGER
    )
''')
conn.commit()
conn.close()
print('✅ Database initialized at', db_path)
"

# Set permissions
echo "🔒 Setting permissions..."
chmod +x start.sh
chmod +x test.sh
chmod +x stop.sh

# Create systemd service file
if [ "$EUID" -eq 0 ]; then
    echo "⚙️  Creating systemd service..."
    cat > /etc/systemd/system/hybrid-agent.service << EOF
[Unit]
Description=Hybrid Agent AI Provider
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$(pwd)
Environment="PATH=$(pwd)/venv/bin:$PATH"
ExecStart=$(pwd)/venv/bin/python -m uvicorn hybrid-agent.api_server:app --host 0.0.0.0 --port 8001
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
    systemctl daemon-reload
    echo "✅ Systemd service created. Enable with: sudo systemctl enable hybrid-agent"
fi

echo "🎉 Installation complete!"
echo ""
echo "Next steps:"
echo "1. Edit config.yaml if needed"
echo "2. Start server: ./start.sh"
echo "3. Test: ./test.sh"
echo ""
echo "API endpoint: http://localhost:8001/v1/chat/completions"
echo "Auth token: hybrid-free-key-2026"