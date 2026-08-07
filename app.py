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

# Chat endpoint with dual-mode logic
@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    try:
        user_msg = req.message.strip()
        if not user_msg:
            raise HTTPException(status_code=400, detail="Message cannot be empty.")

        # Dual mode + shortcuts
        if user_msg.lower().startswith("chat:"):
            result = agent.simple_chat(user_msg[5:].strip())

        elif user_msg.lower().startswith("n8n:"):
            use_case = user_msg[4:].strip()
            if not use_case:
                return ChatResponse(response="Theek hai 👍 — kis use‑case ke liye workflow chahiye? (e.g. Google Sheets → Slack)")
            result = capabilities.generate_n8n_workflow(use_case)
            result = f"Got it ✅ — workflow ready:\n{result}"

        elif user_msg.lower().startswith("analysis:"):
            topic = user_msg[9:].strip()
            if not topic:
                return ChatResponse(response="Analysis kis topic par chahiye?")
            result = capabilities.perform_business_analysis(topic)
            result = f"Here’s your friendly analysis report 📊:\n{result}"

        else:
            result = agent.run(user_msg)
            result = f"Done ✅ — here’s what I found:\n{result}"

        return ChatResponse(response=result)

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
