from fastapi import FastAPI, Request
from pydantic import BaseModel
import uvicorn
from orchestrator_v2 import EnhancedHybridAgent
import os

app = FastAPI()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str = "gpt-4o"
    messages: list[ChatMessage]
    temperature: float = 0

@app.get("/")
def read_root():
    return {"status": "Hybrid Agent API is running"}

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    # Lấy nội dung message cuối cùng của user
    user_request = request.messages[-1].content
    
    agent = EnhancedHybridAgent()
    final_result = agent.run(user_request)
    
    # Format response theo chuẩn OpenAI
    return {
        "id": agent.session_id,
        "object": "chat.completion",
        "created": 123456789,
        "model": request.model,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": final_result
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
