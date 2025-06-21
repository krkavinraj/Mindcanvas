"""
Orchestrator Agent - The central coordinator for the MindCanvas agent system.
Uses LangGraph to manage workflow between planner, coder, and executor agents.
"""
from dotenv import load_dotenv
import os
from typing import Dict, Any

# Import the LangGraph workflow
from app.agents.langgraph_workflow import run_workflow

# Ensure environment variables are loaded
load_dotenv()

async def process_command(input_text: str, input_type: str = "text") -> Dict[str, Any]:
    """
    Process user commands through the LangGraph multi-agent system
    
    Args:
        input_text: User's text or transcribed voice input
        input_type: Input type (text or voice)
    
    Returns:
        Dict containing the generated feature as JSX/React component
    """
    print(f"Processing {input_type} input: {input_text}")

    try:
        # Run the entire workflow through LangGraph
        result = await run_workflow(input_text, input_type)
        print(f"Workflow completed with result type: {result.get('type', 'unknown')}")
        
        return result
    except Exception as e:
        print(f"Error in LangGraph workflow: {str(e)}")
        return {
            "type": "error",
            "message": "I encountered an error while building your feature.",
            "error": str(e)
        }
