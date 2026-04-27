#!/usr/bin/env python3
"""
Hybrid Agent GUI Installer
Run: python3 installer_gui.py
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import os
import sys
import platform
import threading

class HybridInstaller:
    def __init__(self, root):
        self.root = root
        self.root.title("Hybrid Agent Installer")
        self.root.geometry("700x500")
        self.root.configure(bg="#0d1117")
        self.root.resizable(False, False)
        
        # Detect OS
        self.os_name = platform.system()
        self.project_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.setup_ui()
        self.check_existing_install()
    
    def setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#161b22", height=80)
        header.pack(fill="x", pady=(0, 20))
        header.pack_propagate(False)
        
        title = tk.Label(header, text="🤖 Hybrid Agent", 
                        font=("Segoe UI", 24, "bold"),
                        bg="#161b22", fg="#58a6ff")
        title.pack(pady=(15, 0))
        
        subtitle = tk.Label(header, text="Zero-Token AI Provider", 
                           font=("Segoe UI", 10),
                           bg="#161b22", fg="#8b949e")
        subtitle.pack()
        
        # Main content
        self.content = tk.Frame(self.root, bg="#0d1117")
        self.content.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Status card
        self.status_card = tk.Frame(self.content, bg="#161b22", 
                                   highlightbackground="#30363d",
                                   highlightthickness=1,
                                   bd=0)
        self.status_card.pack(fill="x", pady=(0, 20))
        
        self.status_label = tk.Label(self.status_card, 
                                    text="⏳ Checking installation...",
                                    font=("Segoe UI", 11),
                                    bg="#161b22", fg="#8b949e",
                                    padx=15, pady=12)
        self.status_label.pack(anchor="w")
        
        # Actions frame
        self.actions_frame = tk.Frame(self.content, bg="#0d1117")
        self.actions_frame.pack(fill="x")
        
        # Install button
        self.install_btn = tk.Button(self.actions_frame,
                                    text="📦 Install Hybrid Agent",
                                    command=self.start_install,
                                    bg="#238636", fg="white",
                                    font=("Segoe UI", 12, "bold"),
                                    padx=30, pady=10,
                                    cursor="hand2",
                                    relief=tk.FLAT)
        self.install_btn.pack(fill="x", pady=(0, 10))
        
        # Start button
        self.start_btn = tk.Button(self.actions_frame,
                                  text="🚀 Start Server",
                                  command=self.start_server,
                                  bg="#1f6feb", fg="white",
                                  font=("Segoe UI", 12, "bold"),
                                  padx=30, pady=10,
                                  cursor="hand2",
                                  relief=tk.FLAT,
                                  state=tk.DISABLED)
        self.start_btn.pack(fill="x", pady=(0, 10))
        
        # Stop button
        self.stop_btn = tk.Button(self.actions_frame,
                                 text="⏹ Stop Server",
                                 command=self.stop_server,
                                 bg="#da3633", fg="white",
                                 font=("Segoe UI", 12, "bold"),
                                 padx=30, pady=10,
                                 cursor="hand2",
                                 relief=tk.FLAT,
                                 state=tk.DISABLED)
        self.stop_btn.pack(fill="x", pady=(0, 10))
        
        # Open Dashboard button
        self.dashboard_btn = tk.Button(self.actions_frame,
                                      text="🌐 Open Dashboard",
                                      command=self.open_dashboard,
                                      bg="#8957e5", fg="white",
                                      font=("Segoe UI", 12, "bold"),
                                      padx=30, pady=10,
                                      cursor="hand2",
                                      relief=tk.FLAT,
                                      state=tk.DISABLED)
        self.dashboard_btn.pack(fill="x", pady=(0, 10))
        
        # Enable autostart
        self.autostart_var = tk.BooleanVar()
        self.autostart_check = tk.Checkbutton(self.content,
                                             text="☑ Start automatically on boot (Linux only)",
                                             variable=self.autostart_var,
                                             bg="#0d1117", fg="#8b949e",
                                             selectcolor="#161b22",
                                             font=("Segoe UI", 10))
        self.autostart_check.pack(anchor="w", pady=(10, 0))
        
        # Log area
        self.log_frame = tk.LabelFrame(self.content, text=" Installation Log ",
                                      bg="#0d1117", fg="#8b949e",
                                      font=("Segoe UI", 9),
                                      padx=5, pady=5)
        self.log_frame.pack(fill="both", expand=True, pady=(15, 0))
        
        self.log_text = scrolledtext.ScrolledText(self.log_frame,
                                                 bg="#0d1117", fg="#c9d1d9",
                                                 font=("Consolas", 9),
                                                 wrap=tk.WORD,
                                                 state=tk.DISABLED,
                                                 height=8)
        self.log_text.pack(fill="both", expand=True)
        
        # Footer
        footer = tk.Frame(self.root, bg="#161b22", height=30)
        footer.pack(fill="x", side=tk.BOTTOM)
        
        footer_text = tk.Label(footer, text="v1.1.0 | OpenSource | github.com/baok1210/hybrid-agent",
                              bg="#161b22", fg="#6e7681",
                              font=("Segoe UI", 8))
        footer_text.pack(pady=5)
    
    def log(self, message, level="INFO"):
        self.log_text.configure(state=tk.NORMAL)
        timestamp = ""
        if level == "ERROR":
            self.log_text.insert(tk.END, f"❌ {message}\n", "error")
        elif level == "SUCCESS":
            self.log_text.insert(tk.END, f"✅ {message}\n", "success")
        else:
            self.log_text.insert(tk.END, f"ℹ {message}\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)
    
    def check_existing_install(self):
        venv_path = os.path.join(self.project_dir, "venv")
        if os.path.exists(venv_path):
            self.status_label.configure(text="✅ Installed", fg="#238636")
            self.install_btn.configure(text="🔄 Reinstall", bg="#6e7681")
            self.start_btn.configure(state=tk.NORMAL)
            self.check_server_status()
        else:
            self.status_label.configure(text="⏳ Not installed", fg="#da3633")
    
    def check_server_status(self):
        try:
            result = subprocess.run(["pgrep", "-f", "uvicorn.*api_server"],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.status_label.configure(text="🟢 Running", fg="#238636")
                self.start_btn.configure(state=tk.DISABLED)
                self.stop_btn.configure(state=tk.NORMAL)
                self.dashboard_btn.configure(state=tk.NORMAL)
                return True
        except:
            pass
        
        self.status_label.configure(text="⏹ Stopped", fg="#8b949e")
        self.start_btn.configure(state=tk.NORMAL)
        self.stop_btn.configure(state=tk.DISABLED)
        self.dashboard_btn.configure(state=tk.DISABLED)
        return False
    
    def start_install(self):
        threading.Thread(target=self._install, daemon=True).start()
    
    def _install(self):
        self.install_btn.configure(state=tk.DISABLED)
        self.log("Starting installation...")
        
        # Check Python version
        py_version = sys.version_info
        if py_version < (3, 8):
            self.log("Python 3.8+ required!", "ERROR")
            self.install_btn.configure(state=tk.NORMAL)
            return
        
        self.log(f"Python {py_version.major}.{py_version.minor}.{py_version.micro} detected")
        
        # Create venv
        venv_path = os.path.join(self.project_dir, "venv")
        self.log("Creating virtual environment...")
        try:
            subprocess.run([sys.executable, "-m", "venv", venv_path],
                         capture_output=True, check=True)
            self.log("Virtual environment created", "SUCCESS")
        except Exception as e:
            self.log(f"Failed to create venv: {e}", "ERROR")
            self.install_btn.configure(state=tk.NORMAL)
            return
        
        # Install dependencies
        self.log("Installing dependencies (this may take a few minutes)...")
        pip_path = os.path.join(venv_path, "bin", "pip")
        if not os.path.exists(pip_path):
            pip_path = os.path.join(venv_path, "Scripts", "pip.exe")
        
        try:
            subprocess.run([pip_path, "install", "-r", "requirements.txt"],
                         cwd=self.project_dir,
                         capture_output=True, check=True)
            self.log("Dependencies installed successfully", "SUCCESS")
        except Exception as e:
            self.log(f"Failed to install dependencies: {e}", "ERROR")
            self.install_btn.configure(state=tk.NORMAL)
            return
        
        # Make scripts executable
        self.log("Setting up scripts...")
        for script in ["install.sh", "start.sh", "stop.sh", "test.sh"]:
            script_path = os.path.join(self.project_dir, script)
            if os.path.exists(script_path):
                os.chmod(script_path, 0o755)
        
        # Create necessary directories
        os.makedirs(os.path.join(self.project_dir, "logs"), exist_ok=True)
        
        self.log("Installation completed!", "SUCCESS")
        self.status_label.configure(text="✅ Installed", fg="#238636")
        self.start_btn.configure(state=tk.NORMAL)
        self.install_btn.configure(text="🔄 Reinstall", bg="#6e7681", state=tk.NORMAL)
        
        # Install systemd service if Linux and autostart enabled
        if self.os_name == "Linux" and self.autostart_var.get():
            self.install_systemd_service()
    
    def install_systemd_service(self):
        self.log("Installing systemd service...")
        service_content = f"""[Unit]
Description=Hybrid Agent AI Provider
After=network.target

[Service]
Type=simple
User={os.getenv('USER')}
WorkingDirectory={self.project_dir}
ExecStart={os.path.join(self.project_dir, 'venv', 'bin', 'python')} -m uvicorn hybrid-agent.api_server:app --host 0.0.0.0 --port 8001
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        service_path = "/tmp/hybrid-agent.service"
        with open(service_path, "w") as f:
            f.write(service_content)
        
        try:
            subprocess.run(["sudo", "mv", service_path, "/etc/systemd/system/hybrid-agent.service"],
                          capture_output=True, check=True)
            subprocess.run(["sudo", "systemctl", "daemon-reload"],
                          capture_output=True, check=True)
            subprocess.run(["sudo", "systemctl", "enable", "hybrid-agent"],
                          capture_output=True, check=True)
            self.log("Systemd service installed. Will start on boot.", "SUCCESS")
        except Exception as e:
            self.log(f"Failed to install systemd service: {e}", "ERROR")
            self.log("You may need to run: sudo systemctl enable hybrid-agent")
    
    def start_server(self):
        threading.Thread(target=self._start_server, daemon=True).start()
    
    def _start_server(self):
        self.start_btn.configure(state=tk.DISABLED)
        self.log("Starting server...")
        
        try:
            if self.os_name == "Windows":
                subprocess.Popen(["start.sh"], cwd=self.project_dir, shell=True)
            else:
                subprocess.Popen(["./start.sh"], cwd=self.project_dir)
            
            import time
            time.sleep(3)
            
            if self.check_server_status():
                self.log("Server started successfully!", "SUCCESS")
                self.log("Dashboard: http://localhost:8001/dashboard")
        except Exception as e:
            self.log(f"Failed to start server: {e}", "ERROR")
            self.start_btn.configure(state=tk.NORMAL)
    
    def stop_server(self):
        self.log("Stopping server...")
        try:
            subprocess.run(["./stop.sh"], cwd=self.project_dir, capture_output=True)
            self.check_server_status()
            self.log("Server stopped", "SUCCESS")
        except Exception as e:
            self.log(f"Error stopping server: {e}", "ERROR")
    
    def open_dashboard(self):
        import webbrowser
        webbrowser.open("http://localhost:8001/dashboard")

def main():
    root = tk.Tk()
    
    # Set icon (if available)
    try:
        root.iconbitmap(os.path.join(os.path.dirname(__file__), "icon.ico"))
    except:
        pass
    
    app = HybridInstaller(root)
    root.mainloop()

if __name__ == "__main__":
    main()
