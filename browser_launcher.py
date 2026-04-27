"""
Auto-launch Chrome with CDP + handle CAPTCHA + multi-AI support
"""

import subprocess
import time
import os
import sys
import signal
import logging
from pathlib import Path
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BrowserLauncher:
    def __init__(self):
        self.process = None
        self.user_data_dir = Path.home() / ".hybrid-agent-chrome"
        self.user_data_dir.mkdir(exist_ok=True)
        
    def launch_chrome(self, urls=None):
        """Launch Chrome with CDP enabled"""
        if urls is None:
            urls = [
                "https://chatgpt.com",
                "https://gemini.google.com",
                "https://claude.ai"
            ]
        
        # Detect Chrome/Chromium path
        chrome_path = self._find_chrome()
        if not chrome_path:
            logger.error("Chrome/Chromium not found. Install: sudo apt install chromium-browser")
            sys.exit(1)
        
        logger.info(f"Using Chrome: {chrome_path}")
        
        # Build command
        cmd = [
            chrome_path,
            f"--remote-debugging-port=9222",
            f"--user-data-dir={self.user_data_dir}",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-background-networking",
            "--disable-breakpad",
            "--disable-client-side-phishing-detection",
            "--disable-default-apps",
            "--disable-hang-monitor",
            "--disable-popup-blocking",
            "--disable-prompt-on-repost",
            "--disable-sync",
            "--enable-automation",
            "--no-service-autorun",
            "--password-store=basic",
            "--use-mock-keychain",
        ]
        
        # Add URLs
        for url in urls:
            cmd.append(url)
        
        try:
            logger.info(f"Launching Chrome with CDP on port 9222...")
            logger.info(f"Opening tabs: {', '.join(urls)}")
            
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid if sys.platform != "win32" else None
            )
            
            # Wait for Chrome to start
            time.sleep(3)
            
            if self.process.poll() is None:
                logger.info("✅ Chrome launched successfully")
                logger.info("📍 CDP endpoint: ws://127.0.0.1:9222")
                logger.info("🔗 Tabs opened:")
                for url in urls:
                    logger.info(f"   - {url}")
                logger.info("\n⚠️  IMPORTANT:")
                logger.info("   1. Log in to each AI service (ChatGPT, Gemini, Claude)")
                logger.info("   2. If CAPTCHA appears, solve it manually")
                logger.info("   3. Keep Chrome open while using Hybrid Agent")
                logger.info("   4. Press Ctrl+C to close Chrome\n")
                return True
            else:
                logger.error("Chrome failed to start")
                return False
                
        except Exception as e:
            logger.error(f"Failed to launch Chrome: {e}")
            return False
    
    def _find_chrome(self):
        """Find Chrome/Chromium executable"""
        candidates = [
            "/usr/bin/google-chrome",
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser",
            "/snap/bin/chromium",
            "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        ]
        
        for path in candidates:
            if os.path.exists(path):
                return path
        
        return None
    
    def close(self):
        """Close Chrome gracefully"""
        if self.process:
            try:
                if sys.platform != "win32":
                    os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                else:
                    self.process.terminate()
                
                self.process.wait(timeout=5)
                logger.info("Chrome closed")
            except Exception as e:
                logger.error(f"Error closing Chrome: {e}")
                if self.process:
                    self.process.kill()

if __name__ == "__main__":
    launcher = BrowserLauncher()
    
    try:
        launcher.launch_chrome()
        # Keep running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("\nClosing Chrome...")
        launcher.close()
        sys.exit(0)
