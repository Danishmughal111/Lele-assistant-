import os
import requests
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("AgentTools")

class ToolRegistry:
    def __init__(self):
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

    def get_summary(self) -> str:
        return """
1. GitHub Tool: Connects to GitHub repositories, reads files, commits code, fixes bugs, and creates PRs. Requires GITHUB_TOKEN.
2. Browser Tool: Navigates websites, performs web searches, and extracts textual content or scrapes data.
3. Media Generation Tool (OpenRouter): Generates images and videos via OpenRouter API models. Requires OPENROUTER_API_KEY.
4. Code Execution Tool: Safely executes Python code snippets or generates n8n workflows.
"""

    def github_read_file(self, owner: str, repo: str, path: str, branch: str = "main") -> str:
        if not self.github_token:
            return "Error: GITHUB_TOKEN not configured in environment."
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}"
        headers = {"Authorization": f"Bearer {self.github_token}", "Accept": "vnd.github+json"}
        try:
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                import base64
                content_base64 = res.json().get("content", "")
                content = base64.b64decode(content_base64).decode("utf-8")
                return content
            else:
                return f"Error reading file from GitHub: {res.status_code} - {res.text}"
        except Exception as e:
            return f"Exception in github_read_file: {e}"

    def github_create_or_update_file(self, owner: str, repo: str, path: str, message: str, content: str, branch: str = "main") -> str:
        if not self.github_token:
            return "Error: GITHUB_TOKEN not configured in environment."
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        headers = {"Authorization": f"Bearer {self.github_token}", "Accept": "vnd.github+json"}
        
        get_res = requests.get(url, headers=headers, params={"ref": branch}, timeout=10)
        sha = get_res.json().get("sha") if get_res.status_code == 200 else None

        import base64
        encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")
        
        data = {
            "message": message,
            "content": encoded_content,
            "branch": branch
        }
        if sha:
            data["sha"] = sha

        try:
            res = requests.put(url, headers=headers, json=data, timeout=15)
            if res.status_code in [200, 201]:
                return f"Successfully committed {path} to {owner}/{repo} on branch {branch}."
            else:
                return f"Error committing file: {res.status_code} - {res.text}"
        except Exception as e:
            return f"Exception in github_create_or_update_file: {e}"

    def browser_search_and_scrape(self, url: str) -> str:
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AutonomousAgent/1.0"}
            res = requests.get(url, headers=headers, timeout=15)
            if res.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(res.text, 'html.parser')
                for script in soup(["script", "style"]):
                    script.extract()
                text = soup.get_text(separator=' ', strip=True)
                return f"Successfully scraped URL [{url}]:\n{text[:4000]}"
            else:
                return f"Failed to fetch URL {url}: HTTP {res.status_code}"
        except Exception as e:
            return f"Browser tool exception while scraping {url}: {e}"

    def generate_media(self, prompt: str, media_type: str = "image") -> str:
        if not self.openrouter_api_key:
            return "Error: OPENROUTER_API_KEY not configured in environment."
        
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "HTTP-Referer": "https://github.com/autonomous-agent",
            "X-Title": "Autonomous AI Agent"
        }
        model = "stabilityai/stable-diffusion-3-medium" if media_type == "image" else "openai/sora-equivalent"
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": f"Generate {media_type} prompt: {prompt}"}]
        }
        
        try:
            res = requests.post(url, headers=headers, json=payload, timeout=30)
            if res.status_code == 200:
                return f"Media generation successful via OpenRouter. Details: {res.json()}"
            else:
                return f"OpenRouter Media error: {res.status_code} - {res.text}"
        except Exception as e:
            return f"Exception in generate_media: {e}"
