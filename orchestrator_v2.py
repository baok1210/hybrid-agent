"""
Enhanced Orchestrator - Phiên bản tối ưu với State Management, Tool Execution, và Error Recovery
"""

import json
import os
import re
import time
import logging
import uuid
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import requests

from tools import TOOL_MAP, ToolRegistry
from state_manager import StateManager

# --- CẤU HÌNH LOGGING ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s'
)
logger = logging.getLogger("HybridAgent")

# --- CẤU HÌNH API ---
OPENCLAW_URL = os.environ.get("OPENCLAW_URL", "http://localhost:8000/v1/chat/completions")
NINEROUTER_URL = os.environ.get("NINEROUTER_URL", "https://api.9router.com/v1/chat/completions")
NINEROUTER_API_KEY = os.environ.get("NINEROUTER_API_KEY", "your_api_key_here")

# HTTP Session với Retry
http_session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
http_session.mount('http://', HTTPAdapter(max_retries=retries))
http_session.mount('https://', HTTPAdapter(max_retries=retries))

# --- SYSTEM PROMPTS ---
THINKER_SYSTEM_PROMPT = """Bạn là Kiến trúc sư hệ thống (Planner). Nhiệm vụ của bạn là lập kế hoạch thực thi từng bước.

CÁC CÔNG CỤ CÓ SẴN:
1. `terminal`: Chạy lệnh bash (tham số: 'command')
2. `read_file`: Đọc file (tham số: 'path', 'offset', 'limit')
3. `write_file`: Ghi file (tham số: 'path', 'content')
4. `list_directory`: Liệt kê thư mục (tham số: 'path')
5. `search_files`: Tìm file (tham số: 'pattern', 'target', 'path')

RÀNG BUỘC TUYỆT ĐỐI:
1. KHÔNG giải thích dài dòng. KHÔNG dùng markdown.
2. PHẢI trả về duy nhất một chuỗi JSON chuẩn.
3. Cấu trúc JSON bắt buộc:
{
  "thought": "Suy nghĩ logic của bạn",
  "next_actions": [
    {"tool": "tên_tool", "args": {"tên_tham_số": "giá_trị"}}
  ],
  "is_completed": false,
  "final_answer": "Câu trả lời (Chỉ ghi khi is_completed = true)"
}
"""

class EnhancedHybridAgent:
    def __init__(self):
        self.session_id = str(uuid.uuid4())[:8]
        self.state_manager = StateManager()
        self.conversation_history = [
            {"role": "system", "content": THINKER_SYSTEM_PROMPT}
        ]
        self.max_steps = 15
        self.current_step = 0
        
        logger.info(f"[🚀] Agent khởi tạo với Session ID: {self.session_id}")
    
    def _extract_json(self, text: str) -> Dict[str, Any]:
        """Trích xuất JSON an toàn từ nội dung LLM"""
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if not match:
            raise ValueError("Không tìm thấy cấu trúc JSON trong phản hồi.")
        
        json_str = match.group(0)
        json_str = json_str.replace('\n', ' ').replace('\\"', '"')
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"[❌] Lỗi cú pháp JSON: {e}")
            raise
    
    def _validate_plan(self, plan: Dict[str, Any]) -> bool:
        """Kiểm tra tính hợp lệ của plan"""
        required_keys = ["thought", "next_actions", "is_completed", "final_answer"]
        for key in required_keys:
            if key not in plan:
                logger.warning(f"[⚠️] Plan thiếu key: {key}")
                return False
        
        if not isinstance(plan["next_actions"], list):
            logger.warning("[⚠️] next_actions phải là list")
            return False
        
        return True
    
    def ask_thinker(self, user_request: str, retry_count: int = 0) -> Dict[str, Any]:
        """Gọi Thinker (OpenClaw) để ra quyết định"""
        if retry_count > 2:
            logger.error("[❌] Vượt quá số lần retry. Dừng.")
            return {"is_completed": True, "final_answer": "Lỗi hệ thống Thinker."}
        
        self.conversation_history.append({"role": "user", "content": user_request})
        
        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "messages": self.conversation_history,
            "temperature": 0.0,
            "max_tokens": 1000
        }
        
        logger.info("[🧠] Thinker đang phân tích...")
        
        try:
            response = http_session.post(OPENCLAW_URL, json=payload, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            if "choices" in data and data["choices"]:
                content = data["choices"][0]["message"]["content"]
                result_text = content.strip()
            else:
                result_text = '{"thought": "Không nhận được nội dung từ Thinker", "next_actions": [], "is_completed": true, "final_answer": "Lỗi phản hồi từ Thinker"}'

            self.conversation_history.append({"role": "assistant", "content": result_text})
            
            plan = self._extract_json(result_text)
            
            if not self._validate_plan(plan):
                logger.warning("[⚠️] Plan không hợp lệ. Yêu cầu sửa lại...")
                error_feedback = "Plan không hợp lệ. Hãy sinh lại JSON chuẩn."
                return self.ask_thinker(error_feedback, retry_count + 1)
            
            logger.debug(f"[🧠] Plan hợp lệ: {plan}")
            return plan
            
        except Exception as e:
            logger.warning(f"[⚠️] Lỗi parse JSON. Kích hoạt Self-Correction... ({e})")
            error_feedback = f"Lỗi JSON: {str(e)}. Hãy sinh lại CHỈ BẰNG JSON."
            return self.ask_thinker(error_feedback, retry_count + 1)
    
    def execute_tool(self, action: Dict[str, Any]) -> str:
        """Thực thi một tool cụ thể"""
        tool_name = action.get("tool", "unknown")
        args = action.get("args", {})
        
        logger.info(f"[⚡] Doer chạy Tool: {tool_name}")
        
        try:
            if tool_name not in TOOL_MAP:
                return f"ERROR: Tool '{tool_name}' không tồn tại."
            
            tool_func = TOOL_MAP[tool_name]
            result = tool_func(**args)
            
            if isinstance(result, dict) and result.get("success"):
                logger.info(f"[✅] Tool {tool_name} thành công")
                return json.dumps(result)
            else:
                logger.warning(f"[⚠️] Tool {tool_name} thất bại: {result}")
                return json.dumps(result)
                
        except Exception as e:
            logger.error(f"[❌] Crash Tool {tool_name}: {e}")
            return json.dumps({"success": False, "error": str(e)})
    
    def run(self, user_prompt: str):
        """Chạy agent với user prompt"""
        logger.info(f"{'='*60}")
        logger.info(f"[🎯] KHỞI ĐỘNG NHIỆM VỤ: {user_prompt}")
        logger.info(f"{'='*60}")
        
        # Tạo session mới
        self.state_manager.create_session(self.session_id, user_prompt)
        
        current_request = user_prompt
        self.current_step = 1
        
        while self.current_step <= self.max_steps:
            logger.info(f"\n{'─'*60}")
            logger.info(f"[📍] BƯỚC {self.current_step}/{self.max_steps}")
            logger.info(f"{'─'*60}")
            
            # 1. Gọi Thinker lấy Plan
            plan = self.ask_thinker(current_request)
            
            if plan.get("is_completed", False):
                logger.info(f"\n{'='*60}")
                logger.info("[✅] HOÀN THÀNH NHIỆM VỤ")
                logger.info(f"{'='*60}")
                logger.info(f"[📝] KẾT QUẢ: {plan.get('final_answer')}")
                
                # Lưu session hoàn thành
                self.state_manager.finish_session(
                    self.session_id, 
                    "completed", 
                    plan.get('final_answer')
                )
                break
            
            actions = plan.get("next_actions", [])
            if not actions:
                logger.warning("[⚠️] Thinker không đưa ra action nào dù chưa hoàn thành. Dừng để tránh lặp vô hạn.")
                self.state_manager.finish_session(
                    self.session_id,
                    "stopped",
                    "Không có action nào được đưa ra."
                )
                break
            
            # 2. Thực thi song song
            execution_results = []
            with ThreadPoolExecutor(max_workers=5) as executor:
                future_to_action = {executor.submit(self.execute_tool, act): act for act in actions}
                
                for future in as_completed(future_to_action):
                    try:
                        result = future.result()
                        execution_results.append(result)
                    except Exception as exc:
                        execution_results.append(json.dumps({"error": str(exc)}))
            
            # 3. Lưu step vào database
            self.state_manager.save_step(
                self.session_id,
                self.current_step,
                plan,
                actions,
                execution_results
            )
            
            # 4. Feedback
            feedback = "Kết quả thực thi (System Feedback):\n" + "\n".join(execution_results)
            logger.info(f"[🔄] Phản hồi {len(actions)} actions lại cho Thinker")
            
            current_request = feedback
            self.current_step += 1
        
        if self.current_step > self.max_steps:
            logger.error(f"[❌] HỦY BỎ: Vượt quá {self.max_steps} bước (Vòng lặp vô hạn)")
            self.state_manager.finish_session(
                self.session_id,
                "failed",
                f"Vượt quá {self.max_steps} bước"
            )
    
    def show_session_history(self):
        """Hiển thị lịch sử session"""
        history = self.state_manager.get_session_history(self.session_id)
        logger.info(f"\n[📊] LỊCH SỬ SESSION {self.session_id}:")
        for step in history:
            logger.info(f"  Bước {step['step']}: {len(step['actions'])} actions")

if __name__ == "__main__":
    agent = EnhancedHybridAgent()
    agent.run("Hãy tạo cho tôi thư mục project_bao")
    agent.show_session_history()
