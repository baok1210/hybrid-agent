"""
Hybrid Agent v4.0 - Local API Gateway (Anti-Captcha + Stealth)
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import asyncio
import logging
from datetime import datetime
import uuid
import yaml
import os
import re
import random

# Import modules
from human_typer import human_typer
from captcha_handler import captcha_handler
from browser_launcher_v2 import StealthLauncher

# Load config
config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# Load selectors
selectors_path = os.path.join(os.path.dirname(__file__), 'selectors.json')
with open(selectors_path, 'r') as f:
    selectors = json.load(f)

# Models
class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    messages: List[Message]
    model: str = "chatgpt"
    stream: Optional[bool] = False

app = FastAPI(title="Hybrid Agent v4.0")
logger = logging.getLogger(__name__)
launcher = StealthLauncher()

class BrowserCDP:
    def __init__(self, cdp_endpoint: str):
        self.cdp_endpoint = cdp_endpoint
        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None
        
    async def connect(self):
        try:
            import urllib.request
            import json
            from playwright.async_api import async_playwright
            
            # Get actual WebSocket URL from CDP - use /json/list to get browser WS
            resp = urllib.request.urlopen(f"{self.cdp_endpoint}/json/version")
            data = json.loads(resp.read().decode())
            ws_endpoint = data["webSocketDebuggerUrl"]
            
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.connect_over_cdp(ws_endpoint)
            
            # Get existing contexts from the browser
            if self._browser.contexts:
                self._context = self._browser.contexts[0]
            else:
                self._context = await self._browser.new_context()
            return True
        except Exception as e:
            print(f"CDP connection error: {e}")
            return False

    async def find_page(self, pattern: str, target_config: Dict):
        # First try to find existing page in any context
        for ctx in self._browser.contexts:
            for page in ctx.pages:
                if pattern in page.url:
                    self._context = ctx
                    self._page = page
                    return page
        
        # If not found, create new page in first context
        if not self._context:
            self._context = await self._browser.new_context()
        self._page = await self._context.new_page()
        await self._page.goto(target_config["url_pattern"], wait_until="networkidle")
        return self._page
        await self._page.goto(target_config["url_pattern"], wait_until="networkidle")
        return self._page

    async def send_human(self, message: str, target_config: Dict):
        page = self._page
        await page.wait_for_load_state("networkidle")
        if await captcha_handler.detect_captcha(page, target_config):
            await captcha_handler.handle_captcha_flow(page, target_config)
        
        # Human Typing
        await human_typer.type_like_human(page, target_config["input_selector"], message)
        await asyncio.sleep(random.uniform(0.5, 1.2))
        await page.click(target_config["submit_selector"])
        return True

    async def wait_res(self, target_config: Dict):
        page = self._page
        stop_sel = target_config["stop_generating_selector"]
        res_sel = target_config["response_container"]
        
        # Wait for stop button to disappear
        start = asyncio.get_event_loop().time()
        while (asyncio.get_event_loop().time() - start) < 60:
            if not await page.query_selector(stop_sel): break
            await asyncio.sleep(1)
            
        els = await page.query_selector_all(res_sel)
        return await els[-1].text_content() if els else ""

browser_automation = BrowserCDP(config["browser"]["cdp_endpoint"])

@app.on_event("startup")
async def startup():
    logging.basicConfig(level=logging.INFO)
    if not await browser_automation.connect():
        launcher.launch()
        await asyncio.sleep(5)
        await browser_automation.connect()

@app.post("/v1/chat/completions")
async def chat(req: ChatCompletionRequest):
    rid = str(uuid.uuid4())[:8]
    prompt = "\n\n".join([f"{m.role}: {m.content}" for m in req.messages])
    
    target = req.model if req.model in selectors else "chatgpt"
    tconf = selectors[target]
    
    await browser_automation.find_page(tconf["url_pattern"], tconf)
    await browser_automation.send_human(prompt, tconf)
    text = await browser_automation.wait_res(tconf)
    
    return {
        "id": f"chatcmpl-{rid}",
        "object": "chat.completion",
        "created": int(datetime.now().timestamp()),
        "model": req.model,
        "choices": [{"message": {"role": "assistant", "content": text.strip()}, "finish_reason": "stop"}]
    }

@app.get("/v1/models")
async def models():
    return {"data": [{"id": k} for k in selectors.keys()]}

@app.get("/health")
async def health():
    return {"status": "ok", "browser": browser_automation._browser is not None}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
