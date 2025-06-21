"""
Planner Agent - Interprets user inputs and creates structured plans for feature development.
Translates natural language to structured intent and feature specifications.
"""
from typing import Dict, Any
import json
import asyncio

# Import our custom Azure OpenAI wrapper
from app.utils.azure_openai_wrapper import AzureOpenAIWrapper

# System prompt for the planner agent
PLANNER_SYSTEM_PROMPT = """You are the Planner Agent for MindCanvas, an application that dynamically creates features based on user intent.
Your job is to interpret what the user wants and create a detailed plan for building that feature.

TASK:
1. Analyze the user's request and identify what feature they want to build
2. Determine if this is a valid request that we can fulfill (we can build UI components like task trackers, note-taking interfaces, timers, etc.)
3. Create a detailed plan for how to build this feature

OUTPUT FORMAT:
Return a JSON object with the following structure:
{
  "valid": boolean, // whether this is a request we can fulfill
  "error_message": string, // only if valid is false, explain why
  "feature_type": string, // e.g., "task tracker", "note taking app", "timer"
  "feature_name": string, // a short descriptive name
  "description": string, // detailed description of what the feature should do
  "ui_elements": [
    {
      "type": string, // e.g., "input", "button", "list"
      "purpose": string, // what this element is for
      "interactions": [string] // what interactions are possible with this element
    }
  ],
  "data_structure": {}, // simple JSON structure to hold the feature's data
  "functionality": [string] // list of functions the component should have
}

Keep your response concise but complete. Focus on understanding exactly what the user wants and translating it into a clear technical plan."""

async def process_intent(user_input: str, llm = None) -> Dict[str, Any]:
    """
    Process user intent and create a feature plan
    
    Args:
        user_input: User's request
        llm: Optional LLM instance (AzureOpenAIWrapper)
        
    Returns:
        Feature plan as a dictionary
    """
    if not llm:
        # Default to GPT-4o if no LLM is provided
        llm = AzureOpenAIWrapper(
            deployment_name="gpt-4o",
            api_version="2024-02-01",
            temperature=0.2
        )
    
    # Create system prompt for the planner agent
    system_prompt = """You are the Planner Agent for MindCanvas, an application that dynamically creates features based on user intent.
Your job is to interpret what the user wants and create a detailed plan for building that feature.

TASK:
1. Analyze the user's request and identify what feature they want to build
2. Determine if this is a valid request that we can fulfill (we can build UI components like task trackers, note-taking interfaces, timers, etc.)
3. Create a detailed plan for how to build this feature

OUTPUT FORMAT:
Return a JSON object with the following structure:
{
  "valid": boolean, // whether this is a request we can fulfill
  "error_message": string, // only if valid is false, explain why
  "feature_type": string, // e.g., "task tracker", "note taking app", "timer"
  "feature_name": string, // a short descriptive name
  "description": string, // detailed description of what the feature should do
  "ui_elements": [
    {
      "type": string, // e.g., "input", "button", "list"
      "purpose": string, // what this element is for
      "interactions": [string] // what interactions are possible with this element
    }
  ],
  "data_structure": {}, // simple JSON structure to hold the feature's data
  "functionality": [string] // list of functions the component should have
}"""
    
    try:
        # Call the Azure OpenAI API directly through our wrapper
        content = await llm.generate(system_prompt, user_input)
        
        # Parse the plan from the LLM response
        # First try to extract JSON if it's wrapped in markdown code blocks
        try:
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].strip()
            else:
                json_str = content
                
            # Clean up the JSON string - remove comments that might be causing parsing errors
            import re
            json_str = re.sub(r'\s*//.*', '', json_str)  # Remove single-line comments
            
            plan = json.loads(json_str)
        except Exception as json_error:
            print(f"JSON parsing error: {str(json_error)}. Falling back to safe default.")
            # If JSON parsing fails, create a default task tracker plan
            plan = {
                "valid": True,
                "feature_type": "task tracker",
                "feature_name": "Basic Task Manager",
                "description": "A simple task tracker to manage your tasks and to-dos.",
                "ui_elements": [
                    {"type": "input", "purpose": "add new task", "interactions": ["text input"]},
                    {"type": "button", "purpose": "add task", "interactions": ["click"]},
                    {"type": "list", "purpose": "display tasks", "interactions": ["mark complete", "delete"]}
                ],
                "data_structure": {"tasks": [{"id": "string", "text": "string", "completed": "boolean"}]},
                "functionality": ["add task", "mark complete", "delete task", "list tasks"]
            }
        
        # Validate minimum required fields
        if not plan.get("feature_type") and plan.get("valid", True):
            plan["valid"] = False
            plan["error_message"] = "Failed to determine feature type from request."
            
        return plan
    
    except Exception as e:
        print(f"Error parsing planner response: {str(e)}")
        # Return fallback plan with error
        return {
            "valid": False,
            "error_message": f"Failed to create plan: {str(e)}",
            "feature_type": "error",
            "feature_name": "Error Processing Request",
            "description": "The system encountered an error while processing your request.",
            "ui_elements": [],
            "data_structure": {},
            "functionality": []
        }
