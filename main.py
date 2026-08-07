import os
import argparse
from dotenv import load
load()

from agent import DeepSeekAgent
from tools import ToolRegistry
from capabilities import BusinessAndAutomationEngine

def main():
    parser = argparse.ArgumentParser(description="Custom Autonomous AI Agent (Manus-style)")
    parser.add_argument("--task", type=str, help="The task or goal for the autonomous agent to execute.")
    parser.add_argument("--n8n", type=str, help="Generate an advanced n8n workflow for a specific use-case.")
    parser.add_argument("--analysis", type=str, help="Perform business analysis on a topic.")
    parser.add_argument("--serve", action="store_true", help="Start FastAPI web server and chatbot UI.")
    args = parser.parse_args()

    print("=== Custom Autonomous AI Agent Initializing ===")
    
    if args.serve:
        import uvicorn
        print("\n[+] Starting FastAPI Web Server & Chatbot Interface on http://localhost:8000 ...")
        uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)
        return

    agent = DeepSeekAgent()
    engine = BusinessAndAutomationEngine()

    if args.n8n:
        print(f"\n[+] Generating advanced n8n workflow for use-case: {args.n8n}")
        workflow = engine.generate_n8n_workflow(args.n8n)
        print("\n=== Generated n8n Workflow JSON ===")
        print(workflow)
        return

    if args.analysis:
        print(f"\n[+] Running business analysis on: {args.analysis}")
        report = engine.perform_business_analysis(args.analysis)
        print("\n=== Business Analysis Report ===")
        print(report)
        return

    if args.task:
        print(f"\n[+] Executing Task: {args.task}\n")
        result = agent.run(args.task)
        print("\n=== Final Deliverable ===")
        print(result)
        return

    parser.print_help()

if __name__ == "__main__":
    main()
