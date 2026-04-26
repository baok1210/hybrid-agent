import json
import os
import re
import time
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional

# --- CẤU HÌNH LOGGING ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger("HybridAgent")

# --- CẤU HÌNH API ---
OPENCLAW_URL = os.environ.get("OPENCLAW_URL", "http://localhost:8000/v1/chat/completions")
NINEROUTER_URL = os.environ.get("NINEROUTER_URL", "https://api.9router.com/v1/chat/completions")
NINEROUTER_API_KEY = os.environ.get("NINEROUTER_API_KEY", "your_api_key_here")

# Thiết lập session HTTP với Retry tự động (giúp chống đứt kết nối mạng/API lỗi tạm thời)
http_session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[ 500, 502, 503, 504 ])
http_session.mount('http://', HTTPAdapter(max_retries=retries))
http_session.mount('https://', HTTPAdapter(max_retries=retries))

# --- SYSTEM PROMPTS ---
THINKER_SYSTEM_PROMPT = """Bạn là Kiến trúc sư hệ thống (Planner). Nhiệm vụ của bạn là lập kế hoạch thực thi từng bước.
CÁC CÔNG CỤ CÓ SẴN:
1. `terminal`: Chạy lệnh bash (tham số: 'command')
2. `web_search`: Tìm kiếm web (tham số: 'query')
3. `read_file`: Đọc nội dung file (tham số: 'path')

RÀNG BUỘC TUYỆT ĐỐI (SẼ BỊ PHẠT NẾU VI PHẠM):
1. KHÔNG được giải thích dài dòng. KHÔNG dùng markdown (```json ... ```).
2. PHẢI trả về duy nhất một chuỗi JSON chuẩn.
3. Cấu trúc JSON bắt buộc:
{
  "thought": "Suy nghĩ logic của bạn hiện tại",
  "next_actions": [
    {"tool": "tên_tool", "args": {"tên_tham_số": "giá_trị"}}
  ],
  "is_completed": false,
  "final_answer": "Câu trả lời gửi cho người dùng (Chỉ ghi khi is_completed = true)"
}
"""

class HybridAgent:
    def __init__(self):
        self.conversation_history = [
            {"role": "system", "content": THINKER_SYSTEM_PROMPT}
        ]
        self.max_steps = 15 # Ngăn vòng lặp vô hạn
        
    def _extract_json(self, text: str) -> Dict[str, Any]:
        """Trích xuất và parse JSON an toàn từ nội dung LLM (chống lỗi rác văn bản)."""
        # Tìm khối bắt đầu bằng { và kết thúc bằng }
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if not match:
            raise ValueError("Không tìm thấy cấu trúc JSON trong phản hồi.")
        
        json_str = match.group(0)
        # Sửa một số lỗi JSON phổ biến do LLM sinh ra
        json_str = json_str.replace('\n', ' ').replace('\\"', '"') 
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Lỗi cú pháp JSON: {e} | Chuỗi gốc: {json_str}")
            raise

    def ask_thinker(self, user_request: str) -> Dict[str, Any]:
        """Gọi phần Thinker (OpenClaw) để ra quyết định."""
        self.conversation_history.append({"role": "user", "content": user_request})
        
        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "messages": self.conversation_history,
            "temperature": 0.0, # Temperature = 0 để JSON ổn định tuyệt đối
            "max_tokens": 1000
        }
        
        logger.info("[🧠 Thinker] Đang phân tích...")
        
        # --- Logic Gọi API thực tế (Đang Mock cho an toàn khi chưa bật OpenClaw) ---
        # response = http_session.post(OPENCLAW_URL, json=payload, timeout=60)
        # response.raise_for_status()
        # result_text = response.json().get('choices', [{}])[0].get('message', {}).get('content', '')
        
        # Mock Logic:
        time.sleep(0.5)
        if "tạo thư mục" in user_request.lower():
            result_text = '{"thought": "Cần tạo thư mục project_bao theo yêu cầu", "next_actions": [{"tool": "terminal", "args": {"command": "mkdir -p ~/project_bao"}}], "is_completed": false, "final_answer": ""}'
        elif "Lỗi JSON" in user_request:
             # Nếu bị feedback lỗi JSON, tự sửa đổi
             result_text = '{"thought": "Sửa lỗi format", "next_actions": [], "is_completed": true, "final_answer": "Đã tự động fix cấu trúc JSON"}'
        else:
            result_text = '{"thought": "Không còn hành động nào", "next_actions": [], "is_completed": true, "final_answer": "Task hoàn tất an toàn."}'
        
        # Lưu kết quả thô vào lịch sử
        self.conversation_history.append({"role": "assistant", "content": result_text})
        
        try:
            plan = self._extract_json(result_text)
            logger.debug(f"[🧠 Thinker] Plan parsed: {plan}")
            return plan
        except Exception as e:
            # TỰ ĐỘNG SỬA LỖI (Self-Correction): Báo lỗi lại cho AI để nó tự sinh lại JSON chuẩn
            logger.warning("[🧠 Thinker] Gặp lỗi Parse JSON. Đang kích hoạt luồng tự sửa lỗi (Self-Correction)...")
            error_feedback = f"Lỗi rớt JSON: {str(e)}. Hãy sinh lại CHỈ BẰNG JSON, tuyệt đối không có văn bản thừa."
            self.conversation_history.append({"role": "user", "content": error_feedback})
            # Đệ quy 1 lần để AI sửa
            return self.ask_thinker("Hãy sửa lại cấu trúc JSON cho hợp lệ.")

    def execute_tool(self, action: Dict[str, Any]) -> str:
        """Thực thi một tool cụ thể (Sẽ gọi 9router Hermes ở thực tế)."""
        tool_name = action.get("tool", "unknown")
        args = action.get("args", {})
        
        logger.info(f"[⚡ Doer] Chạy Tool: {tool_name} | Tham số: {args}")
        
        # Tương lai: Gọi API 9Router gửi tool_calls tại đây
        # response = http_session.post(NINEROUTER_URL, headers={"Authorization": f"Bearer {NINEROUTER_API_KEY}"}, ...)
        
        try:
            if tool_name == "terminal":
                cmd = args.get("command", "")
                # Dùng os.popen để lấy kết quả thật nếu cần (Lưu ý bảo mật trong thực tế)
                result = os.popen(cmd).read()
                return f"SUCCESS: Lệnh chạy xong. Output: {result}"
            else:
                return f"ERROR: Tool '{tool_name}' không tồn tại."
        except Exception as e:
            logger.error(f"[⚡ Doer] Lỗi Crash Tool {tool_name}: {e}")
            return f"ERROR: Thực thi thất bại: {str(e)}"

    def run(self, user_prompt: str):
        logger.info(f"=== KHỞI ĐỘNG NHIỆM VỤ: {user_prompt} ===")
        current_request = user_prompt
        step = 1
        
        while step <= self.max_steps:
            logger.info(f"--- BƯỚC {step} ---")
            
            # 1. Gọi Thinker lấy Plan
            plan = self.ask_thinker(current_request)
            
            if plan.get("is_completed", False):
                logger.info("=== HOÀN THÀNH NHIỆM VỤ ===")
                logger.info(f"KẾT QUẢ: {plan.get('final_answer')}")
                break
                
            actions = plan.get("next_actions", [])
            if not actions:
                logger.warning("Thinker không đưa ra action nào dù is_completed=False. Ép dừng để tránh lặp vô hạn.")
                break
                
            # 2. XỬ LÝ SONG SONG (Tối ưu tốc độ)
            # Giả sử có nhiều hành động độc lập (như check 2 link cùng lúc), chạy multi-threading
            execution_results = []
            with ThreadPoolExecutor(max_workers=5) as executor:
                # Giao việc cho các luồng
                future_to_action = {executor.submit(self.execute_tool, act): act for act in actions}
                
                for future in as_completed(future_to_action):
                    try:
                        result = future.result()
                        execution_results.append(result)
                    except Exception as exc:
                        execution_results.append(f"EXCEPTION: {str(exc)}")
                        
            # 3. Tổng hợp và Feedback
            feedback = "Kết quả thực thi (System Feedback):\n" + "\n".join(execution_results)
            logger.info(f"[🔄 Feedback Loop] Phản hồi kết quả lại cho Thinker ({len(actions)} actions)")
            
            current_request = feedback
            step += 1
            
        if step > self.max_steps:
            logger.error("=== HỦY BỎ: Vượt quá số bước tối đa (Vòng lặp vô hạn). ===")

if __name__ == "__main__":
    agent = HybridAgent()
    agent.run("Hãy tạo cho tôi thư mục project_bao")
