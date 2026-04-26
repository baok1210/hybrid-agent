"""
State Manager - Quản lý trạng thái session, lịch sử, và memory của agent
Giúp agent nhớ được context giữa các lần chạy và tránh lặp lại công việc
"""

import json
import sqlite3
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

class StateManager:
    """Quản lý trạng thái persistent của agent"""
    
    def __init__(self, db_path: str = "~/.hybrid_agent/state.db"):
        self.db_path = os.path.expanduser(db_path)
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Khởi tạo database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Bảng lưu session
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                status TEXT,
                user_prompt TEXT,
                final_result TEXT
            )
        """)
        
        # Bảng lưu từng bước thực thi
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS steps (
                step_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                step_number INTEGER,
                thinker_plan TEXT,
                actions_executed TEXT,
                execution_results TEXT,
                timestamp TIMESTAMP,
                FOREIGN KEY(session_id) REFERENCES sessions(session_id)
            )
        """)
        
        # Bảng lưu memory (kiến thức học được)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory (
                memory_id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE,
                value TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def create_session(self, session_id: str, user_prompt: str) -> bool:
        """Tạo session mới"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO sessions (session_id, created_at, updated_at, status, user_prompt)
                VALUES (?, ?, ?, ?, ?)
            """, (session_id, datetime.now(), datetime.now(), "running", user_prompt))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Lỗi tạo session: {e}")
            return False
    
    def save_step(self, session_id: str, step_number: int, thinker_plan: Dict, 
                  actions: List[Dict], results: List[str]) -> bool:
        """Lưu thông tin từng bước thực thi"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO steps (session_id, step_number, thinker_plan, actions_executed, execution_results, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                step_number,
                json.dumps(thinker_plan),
                json.dumps(actions),
                json.dumps(results),
                datetime.now()
            ))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Lỗi lưu step: {e}")
            return False
    
    def finish_session(self, session_id: str, status: str, final_result: str) -> bool:
        """Đánh dấu session hoàn thành"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE sessions 
                SET status = ?, final_result = ?, updated_at = ?
                WHERE session_id = ?
            """, (status, final_result, datetime.now(), session_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Lỗi finish session: {e}")
            return False
    
    def save_memory(self, key: str, value: Any) -> bool:
        """Lưu kiến thức vào memory (dùng cho learning)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO memory (key, value, created_at, updated_at)
                VALUES (?, ?, ?, ?)
            """, (key, json.dumps(value), datetime.now(), datetime.now()))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Lỗi lưu memory: {e}")
            return False
    
    def get_memory(self, key: str) -> Optional[Any]:
        """Lấy kiến thức từ memory"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM memory WHERE key = ?", (key,))
            result = cursor.fetchone()
            conn.close()
            if result:
                return json.loads(result[0])
            return None
        except Exception as e:
            print(f"Lỗi lấy memory: {e}")
            return None
    
    def get_session_history(self, session_id: str) -> List[Dict]:
        """Lấy lịch sử tất cả các bước của một session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT step_number, thinker_plan, actions_executed, execution_results, timestamp
                FROM steps
                WHERE session_id = ?
                ORDER BY step_number ASC
            """, (session_id,))
            rows = cursor.fetchall()
            conn.close()
            
            history = []
            for row in rows:
                history.append({
                    "step": row[0],
                    "plan": json.loads(row[1]),
                    "actions": json.loads(row[2]),
                    "results": json.loads(row[3]),
                    "timestamp": row[4]
                })
            return history
        except Exception as e:
            print(f"Lỗi lấy history: {e}")
            return []
    
    def get_all_sessions(self, limit: int = 10) -> List[Dict]:
        """Lấy danh sách sessions gần đây"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT session_id, created_at, status, user_prompt, final_result
                FROM sessions
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            conn.close()
            
            sessions = []
            for row in rows:
                sessions.append({
                    "session_id": row[0],
                    "created_at": row[1],
                    "status": row[2],
                    "prompt": row[3],
                    "result": row[4]
                })
            return sessions
        except Exception as e:
            print(f"Lỗi lấy sessions: {e}")
            return []
