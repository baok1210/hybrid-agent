# Hybrid Agent v3.0 - Local API Gateway

## 🎯 What is this?

Local API Gateway that automates Web UI interactions (ChatGPT/Claude) via Chrome DevTools Protocol (CDP) and returns OpenAI-compatible JSON responses.

**Key Features:**
- ✅ OpenAI-compatible API endpoint (`/v1/chat/completions`)
- ✅ Function calling support with JSON schema enforcement
- ✅ Zero token cost (uses free Web UI via Playwright + CDP)
- ✅ Connects to existing Chrome instance (no new browser windows)
- ✅ Configurable CSS selectors for different Web UIs

## 🚀 Quick Start

### Prerequisites
```bash
# Install Python 3.9+
# Install Google Chrome
```

### Installation
```bash
git clone https://github.com/baok1210/hybrid-agent.git
cd hybrid-agent
chmod +x install.sh
./install.sh
```

### 1. Start Chrome with Remote Debugging
```bash
# Linux
google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug

# macOS
open -a "Google Chrome" --args --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug

# Windows
chrome.exe --remote-debugging-port=9222 --user-data-dir=%TEMP%\chrome-debug
```

### 2. Open ChatGPT Web UI
- Navigate to `https://chat.openai.com`
- Log in to your account
- Keep the tab open

### 3. Start Hybrid Agent
```bash
./start.sh
```

### 4. Test
```bash
./test.sh
```

## 📡 API Usage

```bash
curl -X POST http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer hybrid-free-key-2026" \
  -d '{
    "model": "hybrid-agent",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

## 🔌 Integration

### Clawx/Hermes
```
Base URL: http://localhost:8001/v1
API Key: hybrid-free-key-2026
Model: hybrid-agent
```

## Project Structure
```
.
├── api_server.py       # FastAPI server with Playwright CDP
├── config.yaml         # Configuration
├── selectors.json      # CSS selectors for Web UIs
├── requirements.txt    # Dependencies
├── install.sh         # Install script
├── start.sh          # Start server
├── stop.sh           # Stop server
└── test.sh           # Test suite
```
