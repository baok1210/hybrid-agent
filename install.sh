#!/bin/bash
# █████████████████████████████████████████████████████████████████
# Hybrid Agent - 1-Click Installer
# Chỉ cần chạy: curl -fsSL ... | bash
# █████████████████████████████████████████████████████████████████

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║           🚀 Hybrid Agent - One Click Install               ║"
echo "║           Zero Token AI + Native Tool Execution               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Step 1: Check Python
echo -e "\n${YELLOW}[1/5]${NC} Kiểm tra Python..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 chưa được cài đặt${NC}"
    echo "Vui lòng cài Python3 trước: https://python.org"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓${NC} Đã tìm thấy Python $PYTHON_VERSION"

# Step 2: Create directory
echo -e "\n${YELLOW}[2/5]${NC} Tạo thư mục..."
INSTALL_DIR="$HOME/hybrid-agent"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"
echo -e "${GREEN}✓${NC} Thư mục: $INSTALL_DIR"

# Step 3: Download files
echo -e "\n${YELLOW}[3/5]${NC} Tải mã nguồn..."

# Create requirements.txt
cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
requests==2.31.0
urllib3==2.1.0
EOF

echo -e "${GREEN}✓${NC} Đã tạo requirements.txt"

# Step 4: Install dependencies
echo -e "\n${YELLOW}[4/5]${NC} Cài đặt thư viện..."
pip3 install -q -r requirements.txt
echo -e "${GREEN}✓${NC} Đã cài xong thư viện"

# Step 5: Create main server file
echo -e "\n${YELLOW}[5/5]${NC} Tạo server..."

cat > server.py << 'SCRIPT'
"""
Hybrid Agent - Zero Token API Server
"""
import json
import os
import re
import subprocess
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import glob

app = FastAPI(title="Hybrid Agent", version="2.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"])

class ChatRequest(BaseModel):
    messages: List[Dict[str, str]]
    model: str = "claude-3-5-sonnet"

class ExecuteRequest(BaseModel):
    tool: str
    args: Dict[str, Any]

# Tool implementations
def run_terminal(command: str) -> dict:
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        return {"success": result.returncode == 0, "output": result.stdout, "error": result.stderr}
    except Exception as e:
        return {"success": False, "error": str(e)}

def read_file(path: str) -> dict:
    try:
        with open(path, 'r') as f:
            return {"success": True, "content": f.read()}
    except Exception as e:
        return {"success": False, "error": str(e)}

def write_file(path: str, content: str) -> dict:
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write(content)
        return {"success": True, "message": f"Đã ghi {path}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def list_dir(path: str = ".") -> dict:
    try:
        items = os.listdir(path)
        return {"success": True, "items": items, "path": os.path.abspath(path)}
    except Exception as e:
        return {"success": False, "error": str(e)}

def search_files(pattern: str, path: str = ".") -> dict:
    try:
        matches = glob.glob(os.path.join(path, pattern), recursive=True)
        return {"success": True, "matches": matches, "count": len(matches)}
    except Exception as e:
        return {"success": False, "error": str(e)}

TOOL_MAP = {
    "terminal": run_terminal,
    "read_file": read_file,
    "write_file": write_file,
    "list_directory": list_dir,
    "search_files": search_files
}

@app.get("/")
def root():
    return {
        "service": "Hybrid Agent",
        "status": "running",
        "endpoints": {
            "/chat/completions": "Thinker + Doer (cần OpenClaw)",
            "/execute": "Direct tool execution (không cần AI)"
        }
    }

@app.post("/execute")
def execute(req: ExecuteRequest):
    """Thực thi tool trực tiếp - Không cần AI"""
    if req.tool not in TOOL_MAP:
        return {"success": False, "error": f"Tool '{req.tool}' không tồn tại"}
    
    result = TOOL_MAP[req.tool](**req.args)
    return result

if __name__ == "__main__":
    print("🌐 Hybrid Agent đang chạy trên http://localhost:8001")
    uvicorn.run(app, host="0.0.0.0", port=8001)
SCRIPT

echo -e "${GREEN}✓${NC} Đã tạo server.py"

# Create launcher script
cat > start.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
echo "🚀 Khởi động Hybrid Agent..."
echo ""
echo "📍 API Endpoint: http://localhost:8001"
echo "📍 Test: curl http://localhost:8001/"
echo ""
python3 server.py
EOF
chmod +x start.sh

# Create quick test
cat > test.sh << 'EOF'
#!/bin/bash
echo "🧪 Test Hybrid Agent..."
curl -s http://localhost:8001/ | python3 -m json.tool
echo ""
echo "✅ Server đang chạy!"
EOF
chmod +x test.sh

# Success message
echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    ✅ CÀI ĐẶT THÀNH CÔNG!                      ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "📂 Thư mục: $INSTALL_DIR"
echo ""
echo "🚀 Cách chạy:"
echo "   cd $INSTALL_DIR"
echo "   ./start.sh"
echo ""
echo "🧪 Test API:"
echo "   curl http://localhost:8001/"
echo "   curl -X POST http://localhost:8001/execute \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"tool\":\"terminal\",\"args\":{\"command\":\"ls -la\"}}'"
echo ""
