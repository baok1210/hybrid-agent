#!/bin/bash
# Hybrid Agent Installation Script

set -e

echo "🚀 Hybrid Agent - Playwright + CDP Gateway"
echo "=========================================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.9+ first."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python $PYTHON_VERSION detected"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate venv
source venv/bin/activate

echo "📦 Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Install Playwright browsers
echo "🌐 Installing Playwright Chromium..."
python -m playwright install chromium

# Create logs directory
mkdir -p logs

# Make scripts executable
chmod +x start.sh stop.sh test.sh

echo ""
echo "🎉 Installation complete!"
echo ""
echo "Next steps:"
echo "1. Start Chrome with remote debugging:"
echo "   google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug"
echo ""
echo "2. Open ChatGPT (https://chat.openai.com) in that Chrome instance"
echo "   and log in to your account."
echo ""
echo "3. Start Hybrid Agent:"
echo "   ./start.sh"
echo ""
echo "4. Test the API:"
echo "   ./test.sh"
echo ""
echo "For Clawx/Hermes integration:"
echo "   Base URL: http://localhost:8001/v1"
echo "   API Key: hybrid-free-key-2026"
echo "   Model: hybrid-agent"
