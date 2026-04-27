import requests
import json
import re
import uuid
import sqlite3
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from tools import tool_registry

class EnhancedHybridAgent:
    def __init__(self, openclaw_url="http://localhost:8000/v1/chat/completions"):
        self.openclaw_url = openclaw_url
        self.session_id = str(uuid.uuid4())
        self.history = []
        self.db_path = os.path.expanduser("~/.hybrid_agent/state.db")
        self._init_db()
        
    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                created_at TEXT,
                user_request TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS steps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                step_num INTEGER,
                thought TEXT,
                actions TEXT,
                results TEXT,
                timestamp TEXT
            )
        """)
        conn.commit()
        conn.close()
        
    def _save_session(self, user_request):
        conn = sqlite3.connect(self.db_path)
        conn.execute("INSERT INTO sessions VALUES (?, ?, ?)", 
                    (self.session_id, datetime.now().isoformat(), user_request))
        conn.commit()
        conn.close()
        
    def _save_step(self, step_num, thought, actions, results):
        conn = sqlite3.connect(self.db_path)
        conn.execute("INSERT INTO steps (session_id, step_num, thought, actions, results, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                    (self.session_id, step_num, thought, json.dumps(actions), json.dumps(results), datetime.now().isoformat()))
        conn.commit()
        conn.close()
        
    def _call_thinker(self, messages):
        """Call OpenClaw for reasoning"""
        try:
            response = requests.post(self.openclaw_url, json={
                "model": "gpt-4o",
                "messages": messages,
                "temperature": 0
            }, timeout=60)
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            # Fallback: mock response for testing without OpenClaw
            return json.dumps({
                "thought": "Executing user request",
                "next_actions": [{"tool": "terminal", "args": {"command": "echo 'Mock response'"}}],
                "is_completed": True,
                "final_answer": "Task completed (mock mode)"
            })
    
    def _extract_json(self, text):
        """Extract JSON from markdown code blocks or raw text"""
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))
        
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        
        return json.loads(text)
    
    def _execute_actions(self, actions):
        """Execute actions concurrently"""
        results = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(tool_registry.call, action["tool"], action["args"]): action for action in actions}
            for future in as_completed(futures):
                action = futures[future]
                try:
                    result = future.result(timeout=30)
                    results.append({"action": action, "result": result})
                except Exception as e:
                    results.append({"action": action, "error": str(e)})
        return results
    
    def run(self, user_request, max_steps=10):
        """Main execution loop"""
        self._save_session(user_request)
        
        system_prompt = """You are a hybrid AI agent. Your job is to think and plan, then output JSON for tool execution.

Output format (strict JSON):
{
  "thought": "Your reasoning about what to do next",
  "next_actions": [
    {"tool": "terminal", "args": {"command": "ls -la"}},
    {"tool": "write_file", "args": {"path": "test.txt", "content": "Hello"}}
  ],
  "is_completed": false,
  "final_answer": "Only when is_completed is true"
}

Available tools: terminal, read_file, write_file, list_directory

Rules:
- Output ONLY valid JSON
- Set is_completed=true when task is done
- Provide final_answer when completed
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_request}
        ]
        
        for step in range(max_steps):
            print(f"\n=== Step {step + 1} ===")
            
            # Think
            raw_response = self._call_thinker(messages)
            print(f"Thinker output: {raw_response[:200]}...")
            
            try:
                plan = self._extract_json(raw_response)
            except Exception as e:
                print(f"JSON parse error: {e}")
                messages.append({"role": "assistant", "content": raw_response})
                messages.append({"role": "user", "content": f"Error parsing JSON: {e}. Please output valid JSON only."})
                continue
            
            thought = plan.get("thought", "")
            actions = plan.get("next_actions", [])
            is_completed = plan.get("is_completed", False)
            final_answer = plan.get("final_answer", "")
            
            print(f"Thought: {thought}")
            
            # Execute
            if actions:
                print(f"Executing {len(actions)} actions...")
                results = self._execute_actions(actions)
                self._save_step(step + 1, thought, actions, results)
                
                # Feedback
                feedback = f"Execution results:\n{json.dumps(results, indent=2)}"
                messages.append({"role": "assistant", "content": raw_response})
                messages.append({"role": "user", "content": feedback})
                print(f"Results: {results}")
            
            # Check completion
            if is_completed:
                print(f"\n✓ Task completed: {final_answer}")
                self.history.append({"request": user_request, "answer": final_answer})
                return final_answer
        
        return "Max steps reached without completion"
    
    def show_session_history(self):
        """Display session execution history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("SELECT step_num, thought, actions, results FROM steps WHERE session_id = ? ORDER BY step_num", (self.session_id,))
        for row in cursor:
            print(f"\nStep {row[0]}: {row[1]}")
            print(f"Actions: {row[2]}")
            print(f"Results: {row[3]}")
        conn.close()

if __name__ == "__main__":
    import os
    agent = EnhancedHybridAgent()
    result = agent.run("Tạo thư mục test_project và ghi file readme.txt với nội dung 'Hello Hybrid Agent'")
    print(f"\nFinal result: {result}")
    agent.show_session_history()
