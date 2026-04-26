"""
Tools Module - Định nghĩa các công cụ thực thi cho Hermes Doer
Mỗi tool là một hàm Python có docstring rõ ràng để Hermes dễ hiểu
"""

import os
import subprocess
from typing import Dict, Any, Optional

class ToolRegistry:
    """Quản lý danh sách tools có sẵn"""
    
    @staticmethod
    def get_available_tools() -> list:
        """Trả về danh sách tools dưới dạng schema cho Hermes"""
        return [
            {
                "name": "terminal",
                "description": "Chạy lệnh bash/shell trên hệ thống. Dùng để thực thi các tác vụ hệ thống.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "Lệnh bash cần chạy"
                        }
                    },
                    "required": ["command"]
                }
            },
            {
                "name": "read_file",
                "description": "Đọc nội dung file văn bản. Hỗ trợ đọc file lớn với pagination.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Đường dẫn tuyệt đối hoặc tương đối đến file"
                        },
                        "offset": {
                            "type": "integer",
                            "description": "Số dòng bắt đầu đọc (mặc định 1)",
                            "default": 1
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Số dòng đọc tối đa (mặc định 500)",
                            "default": 500
                        }
                    },
                    "required": ["path"]
                }
            },
            {
                "name": "write_file",
                "description": "Ghi nội dung vào file. Tự động tạo thư mục nếu chưa tồn tại.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Đường dẫn đến file cần ghi"
                        },
                        "content": {
                            "type": "string",
                            "description": "Nội dung cần ghi"
                        }
                    },
                    "required": ["path", "content"]
                }
            },
            {
                "name": "list_directory",
                "description": "Liệt kê các file và thư mục trong một thư mục.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Đường dẫn thư mục (mặc định là thư mục hiện tại)"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "search_files",
                "description": "Tìm file theo pattern hoặc nội dung.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pattern": {
                            "type": "string",
                            "description": "Pattern tìm kiếm (glob hoặc regex)"
                        },
                        "target": {
                            "type": "string",
                            "description": "'files' để tìm file, 'content' để tìm trong nội dung",
                            "default": "files"
                        },
                        "path": {
                            "type": "string",
                            "description": "Thư mục bắt đầu tìm kiếm",
                            "default": "."
                        }
                    },
                    "required": ["pattern"]
                }
            }
        ]

# --- IMPLEMENTATION CỦA CÁC TOOLS ---

def run_terminal(command: str) -> Dict[str, Any]:
    """Thực thi lệnh terminal và trả về kết quả"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=30
        )
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr,
            "exit_code": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output": "",
            "error": "Lệnh chạy quá 30 giây",
            "exit_code": -1
        }
    except Exception as e:
        return {
            "success": False,
            "output": "",
            "error": str(e),
            "exit_code": -1
        }

def read_file(path: str, offset: int = 1, limit: int = 500) -> Dict[str, Any]:
    """Đọc file với pagination"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            total_lines = len(lines)
            start = max(0, offset - 1)
            end = min(total_lines, start + limit)
            content = ''.join(lines[start:end])
            
            return {
                "success": True,
                "content": content,
                "total_lines": total_lines,
                "read_lines": end - start
            }
    except FileNotFoundError:
        return {"success": False, "error": f"File không tồn tại: {path}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def write_file(path: str, content: str) -> Dict[str, Any]:
    """Ghi file với tự động tạo thư mục"""
    try:
        # Tạo thư mục nếu chưa tồn tại
        dir_path = os.path.dirname(path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return {"success": True, "message": f"Đã ghi thành công vào {path}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def list_directory(path: str = ".") -> Dict[str, Any]:
    """Liệt kê nội dung thư mục"""
    try:
        items = os.listdir(path)
        files = []
        dirs = []
        for item in items:
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                dirs.append(item + "/")
            else:
                files.append(item)
        
        return {
            "success": True,
            "path": os.path.abspath(path),
            "files": files,
            "directories": dirs,
            "total": len(items)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def search_files(pattern: str, target: str = "files", path: str = ".") -> Dict[str, Any]:
    """Tìm file theo pattern"""
    try:
        if target == "files":
            # Tìm file theo glob pattern
            import glob
            full_pattern = os.path.join(path, pattern)
            matches = glob.glob(full_pattern, recursive=True)
            return {"success": True, "matches": matches, "count": len(matches)}
        else:
            # Tìm trong nội dung file
            import re
            matches = []
            for root, _, files in os.walk(path):
                for file in files:
                    if file.endswith(('.py', '.md', '.txt', '.json', '.yaml', '.yml')):
                        try:
                            with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                                content = f.read()
                                if re.search(pattern, content):
                                    matches.append(os.path.join(root, file))
                        except:
                            pass
            return {"success": True, "matches": matches, "count": len(matches)}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Map tool name -> function
TOOL_MAP = {
    "terminal": run_terminal,
    "read_file": read_file,
    "write_file": write_file,
    "list_directory": list_directory,
    "search_files": search_files
}
