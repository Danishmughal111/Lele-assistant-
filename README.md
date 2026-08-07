# Autonomous AI Agent (Manus-Style)

A complete, production-ready autonomous AI agent project featuring a modern web-based chatbot interface, integrated DeepSeek reasoning, GitHub automation, web browsing, and advanced n8n workflow generation.

---

## 📁 Project Structure

```
autonomous_agent/
├── main.py            # CLI entry point
├── app.py             # FastAPI backend server
├── agent.py           # Core agent loop (DeepSeek)
├── tools.py           # GitHub, Browser, Media tools
├── capabilities.py    # n8n & Business engine
├── requirements.txt   # Project dependencies
├── .env.example       # API key template
└── static/            # Web Frontend (Chatbot UI)
    ├── index.html     # Chat UI
    ├── style.css      # Modern dark styling
    └── script.js      # Chat logic & Markdown parser
```

---

## 🚀 Quick Setup (Non-Developer Friendly)

### 1. Prerequisites
- **Python 3.10+**: Download from [python.org](https://www.python.org/).

### 2. Installation
Open your terminal in the project folder and run:
```bash
pip install -r requirements.txt
```

### 3. Configuration
1. Rename `.env.example` to `.env`.
2. Open `.env` and add your API keys:
   - **DEEPSEEK_API_KEY**: Get it from [platform.deepseek.com](https://platform.deepseek.com/).
   - **OPENROUTER_API_KEY**: Get it from [openrouter.ai](https://openrouter.ai/).
   - **GITHUB_TOKEN**: Generate a Personal Access Token from GitHub settings.

---

## 🖥️ How to Use

### Option A: Web Interface (Recommended)
Start the modern chatbot interface:
```bash
python main.py --serve
```
Then open **http://localhost:8000** in your browser.

### Option B: Command Line Interface (CLI)
- **Autonomous Task:** `python main.py --task "Your complex task here"`
- **n8n Workflow:** `python main.py --n8n "Sync Shopify to Slack"`
- **Business Analysis:** `python main.py --analysis "Market expansion strategy"`

---

## 🛠️ Advanced Features
- **Intelligent Planning:** The agent breaks down tasks into steps before execution.
- **Tool Execution:** Real-world interaction with GitHub, Websites, and Media APIs.
- **n8n Expert:** Generates valid JSON workflows for direct import into n8n.
- **Modern UI:** Responsive dark-themed chat interface with markdown support.

---

## ☁️ Deployment (Render.com)
1. Push to GitHub.
2. Create **Web Service** on Render.
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn app:app --host 0.0.0.0 --port 8000`
5. Add Environment Variables in Render Dashboard.
