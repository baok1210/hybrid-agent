# Hybrid Agent AI Provider

OpenAI-compatible API provider that uses OpenClaw's zero-token approach for free reasoning + local tool execution.

## Features
- **OpenAI-compatible API**: `/v1/chat/completions` endpoint
- **Zero-token reasoning**: Uses OpenClaw Web UI for free AI thinking
- **Local tool execution**: Terminal, file I/O, directory listing
- **Persistent sessions**: SQLite database for state management
- **Mock reasoning**: Fallback mode when OpenClaw is unavailable
- **Authentication**: Bearer token protection
- **Health monitoring**: `/health` endpoint with metrics
- **Rate limiting**: Per-IP request limiting
- **Logging**: Structured logging with rotation
- **Docker support**: Containerized deployment

## Quick Start

### 1. Install
```bash
git clone https://github.com/baok1210/hybrid-agent.git
cd hybrid-agent
./install.sh
```

### 2. Configure
Edit `config.yaml`:
```yaml
api:
  port: 8001
  auth_token: "hybrid-free-key-2026"
openclaw:
  url: "http://localhost:18789/v1/chat/completions"
  enabled: true
tools:
  timeout: 30
  max_workers: 5
logging:
  level: "INFO"
  file: "logs/hybrid-agent.log"
```

### 3. Start
```bash
./start.sh
# or with Docker
docker-compose up -d
```

### 4. Test
```bash
./test.sh
# or manual curl
curl -X POST http://localhost:8001/v1/chat/completions \
  -H "Authorization: Bearer hybrid-free-key-2026" \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Hello"}]}'
```

## API Reference

### Authentication
```
Authorization: Bearer <token>
```

### Endpoints
- `POST /v1/chat/completions` - Main chat completion endpoint
- `GET /health` - Health check with metrics
- `GET /metrics` - Prometheus metrics
- `GET /sessions` - List active sessions
- `DELETE /sessions/{id}` - Delete session

### Request Format
```json
{
  "model": "hybrid-agent",
  "messages": [
    {"role": "user", "content": "Your request"}
  ],
  "temperature": 0,
  "max_tokens": 1000
}
```

### Response Format
```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "hybrid-agent",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Response"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  }
}
```

## Architecture

```
┌─────────────────────────────────────────────────┐
│                 Client Application              │
│  (Clawx, Hermes, OpenAI SDK, curl, etc.)       │
└──────────────────────┬──────────────────────────┘
                       │ HTTP POST /v1/chat/completions
                       │ Authorization: Bearer <token>
┌──────────────────────▼──────────────────────────┐
│            Hybrid Agent API Server              │
│  • FastAPI (Python)                             │
│  • Authentication & Rate Limiting              │
│  • Request Validation                           │
│  • Session Management                          │
└──────────────────────┬──────────────────────────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
┌────────▼────┐ ┌──────▼──────┐ ┌────▼──────────┐
│   Thinker   │ │   Doer      │ │   State       │
│  (OpenClaw) │ │  (Tools)    │ │  (SQLite)     │
│  • Reasoning│ │  • Terminal │ │  • Sessions   │
│  • Planning │ │  • File I/O │ │  • History    │
│  • Logic    │ │  • Exec     │ │  • Metrics    │
└─────────────┘ └─────────────┘ └──────────────┘
```

## Configuration

### Environment Variables
```bash
export HYBRID_API_PORT=8001
export HYBRID_AUTH_TOKEN="your-token-here"
export HYBRID_OPENCLAW_URL="http://localhost:18789/v1/chat/completions"
export HYBRID_LOG_LEVEL="INFO"
```

### Config File (`config.yaml`)
```yaml
api:
  host: "0.0.0.0"
  port: 8001
  auth_token: "hybrid-free-key-2026"
  rate_limit_per_minute: 60
  cors_origins: ["*"]

openclaw:
  url: "http://localhost:18789/v1/chat/completions"
  enabled: true
  timeout: 60
  retry_attempts: 3

tools:
  timeout: 30
  max_workers: 5
  allowed_commands: ["ls", "cat", "mkdir", "touch", "echo"]
  blocked_commands: ["rm -rf", "dd", "shutdown"]

database:
  path: "~/.hybrid_agent/state.db"
  backup_interval: 3600

logging:
  level: "INFO"
  file: "logs/hybrid-agent.log"
  max_size_mb: 100
  backup_count: 5

monitoring:
  enable_metrics: true
  enable_health: true
  prometheus_port: 9090
```

## Development

### Setup Development Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Run Tests
```bash
pytest tests/
```

### Code Style
```bash
black .
isort .
flake8 .
```

### Build Docker Image
```bash
docker build -t hybrid-agent .
docker run -p 8001:8001 hybrid-agent
```

## Deployment

### Docker Compose
```yaml
version: '3.8'
services:
  hybrid-agent:
    image: hybrid-agent:latest
    ports:
      - "8001:8001"
    environment:
      - HYBRID_AUTH_TOKEN=${HYBRID_AUTH_TOKEN}
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

### Systemd Service
```ini
[Unit]
Description=Hybrid Agent AI Provider
After=network.target

[Service]
Type=simple
User=hybrid
WorkingDirectory=/opt/hybrid-agent
EnvironmentFile=/etc/hybrid-agent/env
ExecStart=/opt/hybrid-agent/venv/bin/python -m uvicorn api_server:app --host 0.0.0.0 --port 8001
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## Troubleshooting

### Common Issues

1. **Server not starting**
   ```bash
   # Check logs
   tail -f logs/hybrid-agent.log
   
   # Check port conflict
   netstat -tlnp | grep :8001
   
   # Check dependencies
   pip list | grep fastapi
   ```

2. **Authentication failed**
   ```bash
   # Verify token
   echo "Token: $HYBRID_AUTH_TOKEN"
   
   # Test with curl
   curl -v http://localhost:8001/health
   ```

3. **OpenClaw connection failed**
   ```bash
   # Check OpenClaw is running
   curl http://localhost:18789/v1/chat/completions
   
   # Disable OpenClaw in config
   openclaw:
     enabled: false
   ```

4. **Tool execution timeout**
   ```bash
   # Increase timeout in config
   tools:
     timeout: 60
   ```

### Logs
Logs are stored in `logs/hybrid-agent.log` with rotation (100MB max, 5 backups).

### Metrics
Prometheus metrics available at `http://localhost:8001/metrics`.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request

## License
MIT License - see LICENSE file for details.

## Support
- GitHub Issues: https://github.com/baok1210/hybrid-agent/issues
- Email: baok1210@gmail.com

## Changelog
See [CHANGELOG.md](CHANGELOG.md) for version history.