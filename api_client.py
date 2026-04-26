"""
API Client - Dùng để test và gọi Hybrid Agent API
Tương tự cách dùng OpenAI client hoặc 9router client
"""

import requests
import json
from typing import Dict, Any, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HybridAgentClient")


class HybridAgentClient:
    """Client để gọi Hybrid Agent API"""
    
    def __init__(self, base_url: str = "http://localhost:8001", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})
    
    def chat_completions(
        self,
        messages: List[Dict[str, str]],
        model: str = "claude-3-5-sonnet-20241022",
        temperature: float = 0.0,
        max_tokens: int = 1000,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Gọi /chat/completions endpoint
        Tương tự OpenAI API
        """
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        response = self.session.post(
            f"{self.base_url}/chat/completions",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def create_agent(self, name: Optional[str] = None, config: Optional[Dict] = None) -> Dict[str, Any]:
        """Tạo agent mới"""
        payload = {"name": name, "config": config}
        response = self.session.post(
            f"{self.base_url}/agents",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def list_agents(self) -> Dict[str, Any]:
        """Liệt kê agents"""
        response = self.session.get(f"{self.base_url}/agents")
        response.raise_for_status()
        return response.json()
    
    def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """Xem agent"""
        response = self.session.get(f"{self.base_url}/agents/{agent_id}")
        response.raise_for_status()
        return response.json()
    
    def update_agent(self, agent_id: str, name: Optional[str] = None, config: Optional[Dict] = None) -> Dict[str, Any]:
        """Cập nhật agent"""
        payload = {"name": name, "config": config}
        response = self.session.put(
            f"{self.base_url}/agents/{agent_id}",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def delete_agent(self, agent_id: str) -> Dict[str, Any]:
        """Xóa agent"""
        response = self.session.delete(f"{self.base_url}/agents/{agent_id}")
        response.raise_for_status()
        return response.json()
    
    def list_sessions(self, limit: int = 10) -> Dict[str, Any]:
        """Liệt kê sessions"""
        response = self.session.get(
            f"{self.base_url}/sessions",
            params={"limit": limit}
        )
        response.raise_for_status()
        return response.json()
    
    def get_session(self, session_id: str) -> Dict[str, Any]:
        """Xem session"""
        response = self.session.get(f"{self.base_url}/sessions/{session_id}")
        response.raise_for_status()
        return response.json()


# --- EXAMPLES ---
if __name__ == "__main__":
    client = HybridAgentClient()
    
    # Test 1: Chat completions
    print("[1] Test chat completions...")
    try:
        response = client.chat_completions(
            messages=[
                {"role": "user", "content": "Tạo thư mục test_api"}
            ]
        )
        print(json.dumps(response, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Lỗi: {e}")
    
    # Test 2: Create agent
    print("\n[2] Test create agent...")
    try:
        response = client.create_agent(name="my_agent")
        print(json.dumps(response, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Lỗi: {e}")
    
    # Test 3: List agents
    print("\n[3] Test list agents...")
    try:
        response = client.list_agents()
        print(json.dumps(response, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Lỗi: {e}")
    
    # Test 4: List sessions
    print("\n[4] Test list sessions...")
    try:
        response = client.list_sessions()
        print(json.dumps(response, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Lỗi: {e}")
