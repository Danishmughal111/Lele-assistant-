import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from agent import DeepSeekAgent
from capabilities import BusinessAndAutomationEngine

app = FastAPI(title="Autonomous AI Agent API", version="1.1.0")

# Middleware for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent and capabilities
agent = DeepSeekAgent()
capabilities = BusinessAndAutomationEngine()

# Request/Response models
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    try:
        user_msg = req.message.strip()
        if not user_msg:
            raise HTTPException(status_code=400, detail="Message cannot be empty.")

        # Agar user "task:" likhe to agent run kare
        if user_msg.lower().startswith("task:"):
            task_text = user_msg[5:].strip()
            result = agent.run(task_text)
            response_text = f"Done ✅ — here’s what I found:\n{result}"

        else:
            # Normal baat cheet friendly chat mode me
            result = agent.simple_chat(user_msg)
            response_text = result

        # ✅ Add copy & regenerate options in response
        return ChatResponse(
            response=response_text + "\n\nOptions: [Copy] [Regenerate]"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# Mount static files for frontend chatbot UI
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir, exist_ok=True)

app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

# Run with uvicorn if executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
