"""
Coder Agent - Generates React component code based on the planner's specifications.
Converts feature plans into working React JSX code that can be rendered in the frontend.
"""
from typing import Dict, Any
import json
import asyncio

# Import our custom Azure OpenAI wrapper
from app.utils.azure_openai_wrapper import AzureOpenAIWrapper

# System prompt for the coder agent
CODER_SYSTEM_PROMPT = """You are the Coder Agent for MindCanvas, an application that dynamically creates features based on user intent.
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
"""

async def generate_code(plan, llm=None) -> str:
    """Generate React component code from a feature plan
    
    Args:
        plan: The feature plan dictionary
        llm: Optional LLM instance (AzureOpenAIWrapper)
        
    Returns:
        Generated React component code as a string
    """
    if not llm:
        # Default to GPT-4.1 for code generation if no LLM is provided
        llm = AzureOpenAIWrapper(
            deployment_name="gpt-4.1",
            api_version="2024-02-01",
            temperature=0.1  # Lower temperature for more precise code generation
        )
    
    # Create system prompt for code generation with improved instructions
    system_prompt = """You are a senior React developer skilled at creating React functional components.

Your task is to create a single React functional component based on the feature plan provided.

REQUIREMENTS:
1. Use React hooks for state management (useState, useEffect)
2. Include all necessary imports (React, hooks, etc.)
3. Use Tailwind CSS for styling (no external CSS imports)
4. Component should be fully functional and handle all user interactions
5. Component MUST be self-contained in a single file
6. Include all necessary event handlers and state variables
7. The component MUST be executable as a standalone - all functions should be defined inside it
8. NEVER rely on any external libraries beyond React itself
9. The component should be visually appealing with proper Tailwind CSS styling

OUTPUT FORMAT:
Only provide a complete, executable React component that can be directly evaluated in the browser.
Start with imports and export the component at the end.
Do not include any explanations, comments or markdown - just the raw React component code.

IMPORTANT: Your code will be executed directly in the browser, so make sure it is valid, syntactically correct, and has all necessary parts!
"""
    
    # Create user prompt with the plan details
    user_prompt = f"""Feature Plan:
{json.dumps(plan, indent=2)}

Create a React component implementing this feature. Make sure it's a complete, standalone component with:
1. All needed imports (React, hooks)
2. Good-looking UI with Tailwind CSS
3. Full functionality for all features in the plan
4. Proper state management
5. All event handlers included

Do NOT include any markdown formatting like ```jsx - just the pure component code."""
    
    try:
        # Call the Azure OpenAI API through our wrapper
        generated_code = await llm.generate(system_prompt, user_prompt)
        
        # Clean up the code - remove markdown formatting if present
        if "```" in generated_code:
            # Try to extract code between triple backticks
            parts = generated_code.split("```")
            if len(parts) >= 3:
                # Get content from the first code block
                code_block = parts[1]
                # Remove language identifier if present
                if code_block.startswith("jsx") or code_block.startswith("javascript"):
                    code_block = code_block.split("\n", 1)[1] if "\n" in code_block else ""
                generated_code = code_block.strip()
            else:
                # Just in case the format is unusual, try to clean it up
                generated_code = generated_code.replace("```jsx", "").replace("```javascript", "").replace("```", "").strip()
        
        # Ensure the code starts with import React
        if not generated_code.startswith("import React"):
            generated_code = "import React, { useState, useEffect } from 'react';\n\n" + generated_code
        
        # Ensure the component is exported
        if not "export default" in generated_code and not "export function" in generated_code:
            # Identify the main component function name
            import re
            function_match = re.search(r'function\s+([A-Za-z0-9_]+)', generated_code)
            if function_match:
                component_name = function_match.group(1)
                generated_code += f"\n\nexport default {component_name};"
        
        return generated_code.strip()
        
    except Exception as e:
        print(f"Error generating code: {str(e)}")
        # Return an error component that can be properly rendered
        error_message = str(e).replace("'", "\"").replace("\n", " ")
        return f"import React from 'react';\n\nfunction ErrorComponent() {{\n  return (\n    <div className=\"p-4 bg-red-50 border border-red-200 rounded-md\">\n      <h3 className=\"text-lg font-semibold text-red-700\">Failed to generate component</h3>\n      <p className=\"text-red-600\">{error_message}</p>\n      <p className=\"text-sm text-gray-500 mt-2\">Please try again with a different request</p>\n    </div>\n  );\n}}\n\nexport default ErrorComponent;"
