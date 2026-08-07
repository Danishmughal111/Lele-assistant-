import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
load_dotenv()

from agent import DeepSeekAgent
from capabilities import BusinessAndAutomationEngine

app = FastAPI(title="Autonomous AI Agent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = DeepSeekAgent()
capabilities = BusinessAndAutomationEngine()

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
        
        # Check if user requested specific shortcut
        if user_msg.lower().startswith("n8n:"):
            use_case = user_msg[4:].strip()
            result = capabilities.generate_n8n_workflow(use_case)
        elif user_msg.lower().startswith("analysis:"):
            topic = user_msg[9:].strip()
            result = capabilities.perform_business_analysis(topic)
        else:
            result = agent.run(user_msg)
            
        return ChatResponse(response=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files for frontend chatbot UI
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir, exist_ok=True)

app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
