"""
CAPTCHA Handler for Hybrid Agent
Auto-detect and handle CAPTCHA challenges
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from playwright.async_api import Page

logger = logging.getLogger(__name__)

class CaptchaHandler:
    """Handle CAPTCHA challenges automatically"""
    
    def __init__(self):
        self.captcha_solved = False
        self.max_attempts = 3
        
    async def detect_captcha(self, page: Page, target_config: Dict[str, Any]) -> bool:
        """Detect if CAPTCHA is present"""
        try:
            captcha_selectors = target_config.get("captcha_detector", "").split(", ")
            
            for selector in captcha_selectors:
                if selector:
                    element = await page.query_selector(selector)
                    if element:
                        logger.warning(f"CAPTCHA detected: {selector}")
                        return True
            
            # Check for CAPTCHA text in page content
            content = await page.content()
            captcha_keywords = ["captcha", "recaptcha", "verify", "robot", "human", "security check"]
            
            for keyword in captcha_keywords:
                if keyword in content.lower():
                    logger.warning(f"CAPTCHA keyword detected: {keyword}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error detecting CAPTCHA: {e}")
            return False
    
    async def wait_for_captcha_solution(self, page: Page, target_config: Dict[str, Any]) -> bool:
        """Wait for user to solve CAPTCHA manually"""
        try:
            wait_time = target_config.get("captcha_wait_ms", 30000) / 1000
            logger.info(f"Waiting {wait_time}s for CAPTCHA solution...")
            
            # Poll for CAPTCHA disappearance
            start_time = asyncio.get_event_loop().time()
            polling_interval = 2
            
            while (asyncio.get_event_loop().time() - start_time) < wait_time:
                # Check if CAPTCHA still present
                captcha_present = await self.detect_captcha(page, target_config)
                
                if not captcha_present:
                    logger.info("✅ CAPTCHA solved (or disappeared)")
                    self.captcha_solved = True
                    return True
                
                await asyncio.sleep(polling_interval)
            
            logger.warning("CAPTCHA timeout - user may need to solve manually")
            return False
            
        except Exception as e:
            logger.error(f"Error waiting for CAPTCHA: {e}")
            return False
    
    async def handle_captcha_flow(self, page: Page, target_config: Dict[str, Any]) -> bool:
        """Complete CAPTCHA handling flow"""
        logger.info("Starting CAPTCHA handling flow...")
        
        # 1. Detect CAPTCHA
        if not await self.detect_captcha(page, target_config):
            logger.info("No CAPTCHA detected")
            return True
        
        # 2. Notify user
        logger.warning("⚠️  CAPTCHA DETECTED!")
        logger.warning("Please solve the CAPTCHA manually in the browser.")
        logger.warning("The system will wait for you to complete it.")
        
        # 3. Wait for solution
        solved = await self.wait_for_captcha_solution(page, target_config)
        
        if solved:
            logger.info("CAPTCHA flow completed successfully")
            return True
        else:
            logger.error("CAPTCHA not solved within timeout")
            return False
    
    async def ensure_no_captcha_before_send(self, page: Page, target_config: Dict[str, Any]) -> bool:
        """Ensure no CAPTCHA before sending message"""
        attempts = 0
        
        while attempts < self.max_attempts:
            if await self.detect_captcha(page, target_config):
                logger.warning(f"CAPTCHA detected (attempt {attempts + 1}/{self.max_attempts})")
                
                # Wait for user to solve
                await self.wait_for_captcha_solution(page, target_config)
                
                # Check again
                if not await self.detect_captcha(page, target_config):
                    logger.info("CAPTCHA cleared after waiting")
                    return True
                
                attempts += 1
                await asyncio.sleep(5)
            else:
                return True
        
        logger.error(f"CAPTCHA persists after {self.max_attempts} attempts")
        return False

# Global instance
captcha_handler = CaptchaHandler()
