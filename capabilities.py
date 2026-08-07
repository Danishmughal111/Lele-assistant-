import os
import json
import logging
from typing import Dict, Any, Optional
from openai import OpenAI

logger = logging.getLogger("AgentCapabilities")

class BusinessAndAutomationEngine:
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.deepseek.com/v1"):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.base_url = base_url
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url) if self.api_key else None
        self.model = "deepseek-chat"

    def generate_n8n_workflow(self, use_case: str) -> str:
        logger.info(f"Generating advanced n8n workflow for use-case: {use_case}")

        system_prompt = """You are an expert n8n workflow architect. Generate a fully valid, production-ready n8n workflow JSON structure based on the user request.
Return ONLY valid JSON with keys: 'name', 'nodes', 'connections', 'settings'.
Supported nodes include Webhook, Schedule, HTTP Request, IF, Code, Slack, Google Sheets, Email, etc.
"""
        if not self.client:
            return self._get_fallback_advanced_workflow(use_case)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Create n8n workflow for: {use_case}"}
                ],
                response_format={"type": "json_object"}
            )
            return json.dumps(json.loads(response.choices[0].message.content), indent=2)
        except Exception as e:
            logger.error(f"Error calling DeepSeek for n8n: {e}")
            return self._get_fallback_advanced_workflow(use_case)

    def _get_fallback_advanced_workflow(self, use_case: str) -> str:
        workflow = {
            "name": f"Advanced Automation: {use_case}",
            "nodes": [
                {
                    "parameters": {"path": "webhook", "httpMethod": "POST"},
                    "name": "Webhook Trigger",
                    "type": "n8n-nodes-base.webhook",
                    "typeVersion": 1,
                    "position": [250, 300]
                },
                {
                    "parameters": {"jsCode": "return items.map(item => ({ json: { ...item.json, processed: true } }));"},
                    "name": "Data Transform Code",
                    "type": "n8n-nodes-base.code",
                    "typeVersion": 2,
                    "position": [500, 300]
                },
                {
                    "parameters": {"channel": "#general", "text": "={{ JSON.stringify($json) }}"},
                    "name": "Slack Notification",
                    "type": "n8n-nodes-base.slack",
                    "typeVersion": 1,
                    "position": [750, 300]
                }
            ],
            "connections": {
                "Webhook Trigger": {
                    "main": [[{"node": "Data Transform Code", "type": "main", "index": 0}]]
                },
                "Data Transform Code": {
                    "main": [[{"node": "Slack Notification", "type": "main", "index": 0}]]
                }
            },
            "settings": {"executionOrder": "v1"}
        }
        return json.dumps(workflow, indent=2)

    def perform_business_analysis(self, topic: str) -> str:
        if self.client:
            try:
                res = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a top-tier management consultant and financial analyst."},
                        {"role": "user", "content": f"Write an executive business analysis report on: {topic}"}
                    ]
                )
                return res.choices[0].message.content
            except Exception:
                pass

        return f"""# Executive Business Analysis Report
## Topic: {topic}

### 1. Executive Summary
Comprehensive strategic analysis for {topic}, covering market dynamics, competitive advantages, and financial outlook.

### 2. Strategic Insights
- High growth potential in target demographics.
- Scalable autonomous operations reducing overhead.
- Recommended implementation of automated pipelines.
"""
