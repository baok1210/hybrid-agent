import asyncio
import random

class HumanTyper:
    def __init__(self):
        self.min_delay = 0.02
        self.max_delay = 0.1
        
    async def type_like_human(self, page, selector, text):
        await page.click(selector)
        await asyncio.sleep(0.5)
        for char in text:
            delay = random.uniform(self.min_delay, self.max_delay)
            await page.keyboard.type(char, delay=int(delay * 1000))
            if random.random() < 0.05:
                await asyncio.sleep(random.uniform(0.1, 0.3))
        await asyncio.sleep(0.5)

human_typer = HumanTyper()
