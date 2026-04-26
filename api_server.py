"""
API Server - Cung cấp HTTP API cho Hybrid Agent giống 9router
Supports: /chat/completions, /agents, /sessions endpoints
"""

import json
import os
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from orchestrator_v2 import EnhancedHybridAgent
from state_manager import StateManager

# --- CẤU HÌNH ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s'
)
logger = logging.getLogger("HybridAgentAPI")

app = FastAPI(
    title="Hybrid Agent API",
    description="API Server cho Hybrid AI Agent (OpenClaw + Hermes)",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- REQUEST MODELS ---
class ChatCompletionRequest(BaseModel):
    model: str = "claude-3-5-sonnet-20241022"
    messages: List[Dict[str, str]]
    temperature: float = 0.0
    max_tokens: int = 1000
    stream: bool = False

class AgentCreateRequest(BaseModel):
    name: Optional[str] = None
    config: Optional[Dict[str, Any]] = None

class AgentUpdateRequest(BaseModel):
    name: Optional[str] = None
    config: Optional[Dict[str, Any]] = None

# --- GLOBAL STATE ---
agent_instances: Dict[str, EnhancedHybridAgent] = {}
state_manager = StateManager()


# --- API ENDPOINTS ---

@app.get("/")
async def root():
    return {
        "service": "Hybrid Agent API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "/chat/completions": "POST - Gọi agent thực thi task",
            "/agents": "GET - Liệt kê agents, POST - Tạo agent mới",
            "/agents/{agent_id}": "GET - Xem agent, PUT - Cập nhật, DELETE - Xóa",
            "/sessions": "GET - Liệt kê sessions",
            "/sessions/{session_id}": "GET - Xem chi tiết session"
        }
    }


@app.post("/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """
    Endpoint giống OpenAI /chat/completions
    Tự động tạo agent mới nếu chưa có, thực thi task và trả về kết quả
    """
    try:
        # Lấy user message
        user_message = None
        for msg in reversed(request.messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break
        
        if not user_message:
            raise HTTPException(status_code=400, detail="Không tìm thấy user message")
        
        # Tạo agent mới hoặc dùng agent mặc định
        agent_id = "default"
        if agent_id not in agent_instances:
            agent_instances[agent_id] = EnhancedHybridAgent()
        
        agent = agent_instances[agent_id]
        
        # Chạy agent
        agent.run(user_message)
        
        # Lấy kết quả từ session
        history = agent.state_manager.get_session_history(agent.session_id)
        
        # Format response giống OpenAI
        response = {
            "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
            "object": "chat.completion",
            "created": int(datetime.now().timestamp()),
            "model": request.model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": history[-1]["plan"].get("final_answer", "") if history else ""
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": len(user_message),
                "completion_tokens": 0,
                "total_tokens": len(user_message)
            }
        }
        
        return response
        
    except Exception as e:
        logger.error(f"[❌] Lỗi chat completion: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agents")
async def list_agents():
    """Liệt kê tất cả agents đang hoạt động"""
    agents_list = []
    for agent_id, agent in agent_instances.items():
        session = state_manager.get_session_history(agent.session_id)
        agents_list.append({
            "id": agent_id,
            "session_id": agent.session_id,
            "status": "active",
            "last_activity": session[-1]["timestamp"] if session else None,
            "total_steps": len(session)
        })
    
    return {"agents": agents_list, "count": len(agents_list)}


@app.post("/agents")
async def create_agent(request: AgentCreateRequest):
    """Tạo agent mới"""
    agent_id = request.name or f"agent_{uuid.uuid4().hex[:6]}"
    
    if agent_id in agent_instances:
        raise HTTPException(status_code=409, detail=f"Agent '{agent_id}' đã tồn tại")
    
    agent_instances[agent_id] = EnhancedHybridAgent()
    agent_instances[agent_id].session_id = agent_id  # Dùng agent_id làm session_id
    
    return {
        "id": agent_id,
        "session_id": agent_id,
        "status": "created",
        "message": f"Agent '{agent_id}' đã được tạo"
    }


@app.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Xem thông tin agent"""
    if agent_id not in agent_instances:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' không tồn tại")
    
    agent = agent_instances[agent_id]
    session = state_manager.get_session_history(agent.session_id)
    
    return {
        "id": agent_id,
        "session_id": agent.session_id,
        "status": "active",
        "total_steps": len(session),
        "last_session": session[-1] if session else None
    }


@app.put("/agents/{agent_id}")
async def update_agent(agent_id: str, request: AgentUpdateRequest):
    """Cập nhật agent"""
    if agent_id not in agent_instances:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' không tồn tại")
    
    if request.name and request.name != agent_id:
        # Rename agent
        agent_instances[request.name] = agent_instances.pop(agent_id)
        agent_id = request.name
    
    return {
        "id": agent_id,
        "status": "updated",
        "message": f"Agent '{agent_id}' đã được cập nhật"
    }


@app.delete("/agents/{agent_id}")
async def delete_agent(agent_id: str):
    """Xóa agent"""
    if agent_id not in agent_instances:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' không tồn tại")
    
    del agent_instances[agent_id]
    
    return {
        "status": "deleted",
        "message": f"Agent '{agent_id}' đã bị xóa"
    }


@app.get("/sessions")
async def list_sessions(limit: int = 10):
    """Liệt kê sessions"""
    sessions = state_manager.get_all_sessions(limit)
    return {"sessions": sessions, "count": len(sessions)}


@app.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Xem chi tiết session"""
    session = state_manager.get_session_history(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' không tồn tại")
    
    return {
        "session_id": session_id,
        "steps": session,
        "total_steps": len(session)
    }


# --- KHỞI ĐỘNG SERVER ---
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Khởi động Hybrid Agent API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host bind (mặc định: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8001, help="Port (mặc định: 8001)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload cho dev")
    
    args = parser.parse_args()
    
    logger.info(f"[🚀] Khởi động Hybrid Agent API Server trên {args.host}:{args.port}")
    uvicorn.run(
        "api_server:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )
