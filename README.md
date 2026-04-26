# Hybrid Agent với API Server

Hybrid AI Agent với API server giống 9router, hỗ trợ HTTP endpoints để gọi agent từ xa.

## Kiến trúc

```
┌─────────────────────────────────────────────────┐
│                 API Client                       │
│  (OpenAI-compatible / 9router-style)             │
└───────────────┬─────────────────────────────────┘
                │ HTTP/JSON
                ▼
┌─────────────────────────────────────────────────┐
│              API Server (FastAPI)               │
│  - /chat/completions                            │
│  - /agents                                      │
│  - /sessions                                    │
└───────────────┬─────────────────────────────────┘
                │ Python calls
                ▼
┌─────────────────────────────────────────────────┐
│           EnhancedHybridAgent                    │
│  - Thinker (OpenClaw/Claude Web UI)              │
│  - Doer (Hermes/9Router)                        │
│  - State Management                             │
└───────────────┬─────────────────────────────────┘
                │ Tool execution
                ▼
┌─────────────────────────────────────────────────┐
│               Tools                              │
│  - terminal, read_file, write_file, etc.        │
└─────────────────────────────────────────────────┘
```

## Cài đặt

```bash
# Clone repository
git clone <your-repo>
cd hybrid_agent

# Cài dependencies
pip3 install -r requirements.txt

# Khởi động server
chmod +x start_server.sh
./start_server.sh
```

## API Endpoints

### 1. Chat Completions (`POST /chat/completions`)
Tương tự OpenAI API, tự động tạo agent và thực thi task.

```bash
curl -X POST "http://localhost:8001/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3-5-sonnet-20241022",
    "messages": [
      {"role": "user", "content": "Tạo thư mục project_test"}
    ],
    "temperature": 0.0
  }'
```

### 2. Agent Management
- `GET /agents` - Liệt kê agents
- `POST /agents` - Tạo agent mới
- `GET /agents/{agent_id}` - Xem agent
- `PUT /agents/{agent_id}` - Cập nhật agent
- `DELETE /agents/{agent_id}` - Xóa agent

### 3. Session Management
- `GET /sessions` - Liệt kê sessions
- `GET /sessions/{session_id}` - Xem chi tiết session

## Client SDK

```python
from api_client import HybridAgentClient

client = HybridAgentClient(base_url="http://localhost:8001")

# Gọi agent
response = client.chat_completions(
    messages=[
        {"role": "user", "content": "Tạo file test.txt với nội dung 'Hello World'"}
    ]
)

# Quản lý agents
agents = client.list_agents()
my_agent = client.create_agent(name="my_agent")

# Xem sessions
sessions = client.list_sessions()
```

## Tính năng nổi bật

### 1. OpenAI-compatible API
- Endpoint `/chat/completions` giống OpenAI
- Response format chuẩn
- Hỗ trợ streaming (tương lai)

### 2. Multi-agent Support
- Tạo nhiều agents độc lập
- Mỗi agent có session riêng
- State persistence với SQLite

### 3. Tool Execution
- Terminal commands
- File operations
- Directory listing
- File search

### 4. State Management
- Session history
- Step-by-step logging
- Memory storage
- Audit trail

## Cấu hình

### Environment Variables
```bash
export OPENCLAW_URL="http://localhost:8000/v1/chat/completions"
export NINEROUTER_URL="https://api.9router.com/v1/chat/completions"
export NINEROUTER_API_KEY="your_api_key"
```

### Server Options
```bash
python3 api_server.py --host 0.0.0.0 --port 8001 --reload
```

## Testing

```bash
# Test API server
python3 api_client.py

# Test endpoints
curl http://localhost:8001/
curl http://localhost:8001/agents
```

## Security Considerations

⚠️ **Production deployment cần**:
- Authentication (API keys)
- Rate limiting
- Input validation
- Command whitelist
- Sandbox containerization

## Roadmap

- [x] Basic API server
- [x] OpenAI-compatible endpoint
- [ ] Authentication
- [ ] Streaming responses
- [ ] WebSocket support
- [ ] Dashboard UI
- [ ] Plugin system
- [ ] Distributed agents

## License

MIT
