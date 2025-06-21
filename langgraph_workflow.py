"""
LangGraph Workflow - Defines the agent workflow using LangGraph
This connects our agents in a proper graph-based workflow system
"""
from typing import Dict, List, Any, TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END
import os
from dotenv import load_dotenv
import asyncio

# Import our custom Azure OpenAI wrapper
from app.utils.azure_openai_wrapper import AzureOpenAIWrapper

# Import our agents
from app.agents.planner import process_intent
from app.agents.coder import generate_code
from app.agents.executor import execute_code

# Load environment variables
load_dotenv()

# Define the state for our graph
class AgentState(TypedDict):
    # Input from user
    input: str
    input_type: str  # 'text' or 'voice'
    
    # Planning phase
    plan: Dict[str, Any]
    planning_error: str
    
    # Coding phase
    code: str
    coding_error: str
    
    # Execution phase
    executed_component: Dict[str, Any]
    execution_error: str
    
    # Final output
    response: Dict[str, Any]

# Initialize the LLMs
def get_planning_llm():
    """Initialize the Azure OpenAI model for planning and execution (GPT-4o)"""
    return AzureOpenAIWrapper(
        deployment_name="gpt-4o",
        api_version="2024-02-01",
        temperature=0.2
    )
    
def get_coding_llm():
    """Initialize the Azure OpenAI model for code generation (GPT-4.1)"""
    return AzureOpenAIWrapper(
        deployment_name="gpt-4.1",
        api_version="2024-02-01",
        temperature=0.1  # Lower temperature for more precise code generation
    )

# Define the planning node
async def planning(state: AgentState) -> AgentState:
    """Process user intent through the planner agent"""
    try:
        # Use GPT-4o for planning (understanding user intent)
        llm = get_planning_llm()
        
        # Create system and user prompts for planning
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
        
        # Generate the plan directly using our wrapper
        plan_json = await llm.generate(system_prompt, state['input'])
        
        try:
            import json
            plan = json.loads(plan_json)
            return {"plan": plan}
        except json.JSONDecodeError:
            return {"planning_error": "Failed to parse JSON response from planning LLM"}
            
    except Exception as e:
        return {"planning_error": str(e)}

# Define the coding node
async def coding(state: AgentState) -> AgentState:
    """Generate code through the coder agent"""
    try:
        if state.get("planning_error"):
            return {"coding_error": "Planning failed"}
        
        # Use GPT-4.1 for code generation
        llm = get_coding_llm()
        
        # Create system and user prompts for coding
        system_prompt = """You are the Coder Agent for MindCanvas, an application that dynamically creates features based on user intent.
Your job is to generate clean, functional React component code based on a feature plan.

TASK:
1. Review the provided feature plan
2. Generate a complete, self-contained React functional component that implements the feature
3. The code must be valid, well-structured, and follow React best practices
4. Include all necessary state management using React hooks
5. Make the component visually appealing and user-friendly with inline Tailwind CSS

IMPORTANT REQUIREMENTS:
1. The component must be COMPLETELY SELF-CONTAINED with all logic and state inside a single component
2. Use ONLY React hooks for state management (useState, useEffect, useCallback, etc.)
3. Use Tailwind CSS for styling (all classes must be inline, NO external CSS)
4. Component must be a functional component, NOT a class component
5. Include proper comments for major sections and complex logic
6. Handle basic error cases and edge conditions

OUTPUT FORMAT:
Return ONLY the complete React component code without any explanation or markdown formatting.
The code should start with 'import React, { useState, ... } from "react";' and end with the export statement."""
        
        # Format the plan details into a user prompt
        user_prompt = f"""Feature Type: {state['plan'].get('feature_type', 'Unknown')}
Feature Name: {state['plan'].get('feature_name', 'Custom Component')}

Feature Description:
{state['plan'].get('description', 'A custom component based on user request.')}

UI Elements:
{state['plan'].get('ui_elements', [])}

Data Structure:
{state['plan'].get('data_structure', {})}

Functionality:
{state['plan'].get('functionality', [])}

Generate a complete React component that implements this feature."""
            
        # Generate the code directly using our wrapper
        code = await llm.generate(system_prompt, user_prompt)
        return {"code": code}
    except Exception as e:
        return {"coding_error": str(e)}

# Define the execution node
async def executing(state: AgentState) -> AgentState:
    """Execute and validate code through the executor agent"""
    try:
        if state.get("coding_error"):
            return {"execution_error": "Coding failed"}
        
        # For validation, we'll use our custom executor agent
        # but also pass the planning LLM for advanced validation if needed
        planning_llm = get_planning_llm()
        
        # We'll use the execute_code function directly
        result = await execute_code(state['code'], planning_llm)
        return {"executed_component": result}
    except Exception as e:
        return {"execution_error": str(e)}

# Define the response formatter
def format_response(state: AgentState) -> AgentState:
    """Format the final response"""
    if state.get("execution_error"):
        return {
            "response": {
                "type": "error",
                "message": f"Error: {state.get('execution_error')}",
                "component": None
            }
        }
    elif state.get("coding_error"):
        return {
            "response": {
                "type": "error",
                "message": f"Error: {state.get('coding_error')}",
                "component": None
            }
        }
    elif state.get("planning_error"):
        return {
            "response": {
                "type": "error",
                "message": f"Error: {state.get('planning_error')}",
                "component": None
            }
        }
    else:
        return {
            "response": {
                "type": "feature",
                "message": f"I've created a {state['plan'].get('feature_type')} for you.",
                "component": state['executed_component'].get('component'),
                "plan": state['plan']
            }
        }

# Define the edge condition for routing
def should_continue(state: AgentState) -> Literal["continue", "error"]:
    """Determine if we should continue to the next agent or end with an error"""
    if state.get("planning_error"):
        return "error"
    elif state.get("coding_error"):
        return "error"
    elif state.get("execution_error"):
        return "error"
    else:
        return "continue"

# Create the workflow graph
def create_agent_workflow():
    """Create and return the LangGraph workflow"""
    # Initialize the graph
    graph = StateGraph(AgentState)
    
    # Add nodes
    graph.add_node("planning", planning)
    graph.add_node("coding", coding)  
    graph.add_node("executing", executing)
    graph.add_node("format_response", format_response)
    
    # Add edges with conditions
    graph.add_edge("planning", "coding")
    graph.add_conditional_edges(
        "planning",
        should_continue,
        {"continue": "coding", "error": "format_response"}
    )
    
    graph.add_edge("coding", "executing")
    graph.add_conditional_edges(
        "coding",
        should_continue,
        {"continue": "executing", "error": "format_response"}
    )
    
    graph.add_edge("executing", "format_response")
    
    graph.add_edge("format_response", END)
    
    # Set the entry point
    graph.set_entry_point("planning")
    
    return graph.compile()

# Create the workflow
agent_workflow = create_agent_workflow()

# Function to run the workflow
async def run_workflow(input_text: str, input_type: str = "text") -> Dict[str, Any]:
    """
    Run the full agent workflow
    
    Args:
        input_text: User's input text
        input_type: Type of input (text or voice)
        
    Returns:
        The final response with generated component
    """
    # Initialize the state
    initial_state = {
        "input": input_text,
        "input_type": input_type
    }
    
    # Run the workflow
    result = await agent_workflow.ainvoke(initial_state)
    
    # Return the response
    return result["response"]
