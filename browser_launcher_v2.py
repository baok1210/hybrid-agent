#!/usr/bin/env python3
"""
Hybrid Agent v4.0 - Stealth Browser Launcher
Configures Chromium to bypass bot detection systems
"""

import subprocess
import time
import os
import sys
import signal
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StealthLauncher:
    def __init__(self):
        self.process = None
        self.user_data_dir = Path.home() / ".hybrid-agent-v4-stealth"
        self.user_data_dir.mkdir(exist_ok=True)
        
    def launch(self):
        """Khởi động trình duyệt với cấu hình tàng hình"""
        urls = [
            "https://chatgpt.com",
            "https://gemini.google.com",
            "https://claude.ai"
        ]
        
        # Tìm đường dẫn chromium
        chrome_path = "/usr/bin/chromium" 
        if not os.path.exists(chrome_path):
            chrome_path = "/usr/bin/google-chrome"
            
        logger.info(f"🚀 Khởi động Stealth Browser: {chrome_path}")
        
        # Các cờ Anti-Bot quan trọng
        flags = [
            chrome_path,
            "--remote-debugging-port=9222",
            f"--user-data-dir={self.user_data_dir}",
            
            # --- Anti-Detection Flags ---
            "--disable-blink-features=AutomationControlled", # Ẩn navigator.webdriver
            "--no-first-run",
            "--no-default-browser-check",
            "--password-store=basic",
            
            # Masking User Agent (giống người dùng Linux thật)
            "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            
            # Giữ session ổn định
            "--disable-extensions",
            "--disable-notifications",
            "--disable-dev-shm-usage",
            "--no-sandbox"
        ] + urls
        
        try:
            self.process = subprocess.Popen(
                flags,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                preexec_fn=os.setsid
            )
            
            # Đợi trình duyệt khởi động và thiết lập CDP
            time.sleep(5)
            
            if self.process.poll() is None:
                logger.info("✅ Trình duyệt Stealth đã sẵn sàng tại port 9222")
                return True
            else:
                logger.error("❌ Trình duyệt không khởi động được")
                return False
                
        except Exception as e:
            logger.error(f"❌ Lỗi khi khởi động trình duyệt: {e}")
            return False

    def stop(self):
        if self.process:
            try:
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                logger.info("🛑 Đã dừng trình duyệt")
            except:
                pass

if __name__ == "__main__":
    launcher = StealthLauncher()
    launcher.launch()
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        launcher.stop()
