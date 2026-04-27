import subprocess
import os

class ToolRegistry:
    def __init__(self):
        self.tools = {
            "terminal": self.terminal,
            "read_file": self.read_file,
            "write_file": self.write_file,
            "list_directory": self.list_directory
        }

    def call(self, tool_name, args):
        if tool_name not in self.tools:
            return {"error": f"Tool {tool_name} not found"}
        try:
            return self.tools[tool_name](**args)
        except Exception as e:
            return {"error": str(e)}

    def terminal(self, command):
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode
        }

    def read_file(self, path):
        if not os.path.exists(path):
            return {"error": "File not found"}
        with open(path, 'r') as f:
            return {"content": f.read()}

    def write_file(self, path, content):
        os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
        with open(path, 'w') as f:
            f.write(content)
        return {"status": "success", "path": path}

    def list_directory(self, path="."):
        return {"files": os.listdir(path)}

tool_registry = ToolRegistry()
