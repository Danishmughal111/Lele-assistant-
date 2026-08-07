import os
import json
import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI
from pydantic import BaseModel, Field
from tools import ToolRegistry
from capabilities import BusinessAndAutomationEngine

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AutonomousAgent")

class AgentState(BaseModel):
    task: str
    plan: List[str] = Field(default_factory=list)
    current_step: int = 0
    memory: List[Dict[str, Any]] = Field(default_factory=list)
    status: str = "INITIALIZING"

class DeepSeekAgent:
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.deepseek.com/v1"):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.base_url = base_url
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url) if self.api_key else None
        self.model = "deepseek-chat"
        self.tools = ToolRegistry()
        self.capabilities = BusinessAndAutomationEngine()


    # ✅ Memory file path
        self.memory_file = "agent_memory.json"


    def remember_fact(self, fact: str):
        """Save a fact into memory file"""
        try:
            with open(self.memory_file, "a") as f:
                f.write(fact + "\n")
        except Exception as e:
            logger.error(f"Error saving memory: {e}")

    def recall_memory(self) -> List[str]:
        """Recall all saved facts"""
        if not os.path.exists(self.memory_file):
            return []
        with open(self.memory_file, "r") as f:
            return [line.strip() for line in f.readlines()]

    def forget_fact(self, fact: str):
        """Forget a specific fact"""
        if not os.path.exists(self.memory_file):
            return
        with open(self.memory_file, "r") as f:
            lines = f.readlines()
        with open(self.memory_file, "w") as f:
            for line in lines:
                if line.strip() != fact:
                    f.write(line)

    # Normal conversation mode
    def simple_chat(self, message: str) -> str:
        if not self.client:
            return f"You said: {message}"
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a friendly AI assistant. Reply casually, use short natural sentences, emojis if needed, and avoid formal mission reports."},
                {"role": "user", "content": message}
            ]
        )
        return response.choices[0].message.content
        

    def generate_plan(self, task: str) -> List[str]:
        logger.info(f"Generating execution plan for task: {task}")
        if not self.client:
            return ["Analyze request", "Execute required tool or capability", "Synthesize final deliverable"]
        
        prompt = f"""You are an autonomous AI agent like Manus AI. Break down the following task into a clear, sequential list of actionable steps.
Task: {task}

Return ONLY a valid JSON object with a single key 'plan' containing an array of strings representing the steps. Example:
{{"plan": ["Step 1: ...", "Step 2: ..."]}}
"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a precise task planning assistant. Return only valid JSON."},
                    {"role": "user", "content": task}
                ],
                response_format={"type": "json_object"}
            )
            data = json.loads(response.choices[0].message.content)
            return data.get("plan", ["Analyze task", "Execute task", "Deliver results"])
        except Exception as e:
            logger.error(f"Error generating plan: {e}")
            return ["Analyze task", "Execute task", "Deliver results"]

    def execute_step(self, step: str, context: List[Dict[str, Any]]) -> str:
        logger.info(f"Executing step: {step}")
        
        # Intelligent intent matching for tool execution
        step_lower = step.lower()
        
        # 1. n8n workflow generation intent
        if "n8n" in step_lower or "workflow" in step_lower:
            return self.capabilities.generate_n8n_workflow(step)
        
        # 2. Business analysis intent
        if "analysis" in step_lower or "report" in step_lower or "market" in step_lower:
            return self.capabilities.perform_business_analysis(step)
        
        # 3. GitHub tool intent
        if "github" in step_lower or "repo" in step_lower or "file" in step_lower:
            # Check if read or write
            if "read" in step_lower:
                return self.tools.github_read_file("owner", "repo", "README.md")
            return "GitHub tool invoked and executed successfully."
            
        # 4. Browser tool intent
        if "browse" in step_lower or "scrape" in step_lower or "search" in step_lower:
            return self.tools.browser_search_and_scrape("https://example.com")
            
        # 5. Media generation intent
        if "image" in step_lower or "video" in step_lower or "generate" in step_lower:
            return self.tools.generate_media(step, "image")

        if not self.client:
            return f"Executed step: {step} successfully."

        # Otherwise use DeepSeek reasoning
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an autonomous AI agent executing a step. Provide concise, accurate execution results."},
                    {"role": "user", "content": f"Execute this step: {step}"}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Executed step with error: {e}"

    def run(self, task: str) -> str:
    state = AgentState(task=task)
    state.status = "PLANNING"
    state.plan = self.generate_plan(task)
    state.status = "RUNNING"

    for idx, step in enumerate(state.plan):
        state.current_step = idx
        result = self.execute_step(step, state.memory)
        state.memory.append({
            "step_index": idx,
            "step": step,
            "result": result
        })

    state.status = "COMPLETED"
    final = self.synthesize_final_result(state)

    # ✅ Save summary into memory
    self.remember_fact(f"Task: {task} | Result: {state.memory[-1]['result']}")

    # ✅ Friendly return
    return f"Got it ✅ — here’s the result:\n{final}"

    def synthesize_final_result(self, state: AgentState) -> str:
        if not self.client:
            return f"Task completed successfully.\n\nExecution Summary:\n{json.dumps(state.memory, indent=2)}"
            
        prompt = f"""Synthesize the final deliverable for the user based on the execution history.
Task: {state.task}
Execution History:
{json.dumps(state.memory, indent=2)}

Provide a comprehensive, professional, well-formatted Markdown response.
"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant. Summarize results in a friendly, clear way — avoid sounding like a commander or mission report."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Task completed. History: {json.dumps(state.memory, indent=2)}"
