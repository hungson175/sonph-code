"""Task tool for delegating work to specialized agents."""

from langchain_core.tools import tool
from typing import Dict, Any


def create_general_purpose_agent():
    """Create a general-purpose agent with specialized system prompt."""
    # Import here to avoid circular import
    from ..core.agent import CodingAgent
    
    agent = CodingAgent()
    
    # Override system prompt for general-purpose agent
    general_purpose_prompt = """You are an agent for Claude Code, Anthropic's official CLI for Claude. Given the user's message, you should use the tools available to complete the task. Do what has been asked; nothing more, nothing less. When you complete the task simply respond with a detailed writeup.

Your strengths:
- Searching for code, configurations, and patterns across large codebases
- Analyzing multiple files to understand system architecture
- Investigating complex questions that require exploring many files
- Performing multi-step research tasks

Guidelines:
- For file searches: Use Grep or Glob when you need to search broadly. Use Read when you know the specific file path.
- For analysis: Start broad and narrow down. Use multiple search strategies if the first doesn't yield results.
- Be thorough: Check multiple locations, consider different naming conventions, look for related files.
- NEVER create files unless they're absolutely necessary for achieving your goal. ALWAYS prefer editing an existing file to creating a new one.
- NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested.
- In your final response always share relevant file names and code snippets. Any file paths you return in your response MUST be absolute. Do NOT use relative paths.
- For clear communication, avoid using emojis.

Available tools:
"""
    
    # Add tools description
    for t in agent.tools:
        general_purpose_prompt += f"- {t.name}: {t.description}\n"
    
    # Update the system prompt
    agent.system_prompt_str = general_purpose_prompt
    agent.messages[0].content = agent._create_cached_message(general_purpose_prompt)
    
    return agent


@tool("Task")
def task(description: str, prompt: str, subagent_type: str) -> str:
    """Launch a new agent to handle complex, multi-step tasks autonomously.

    ## Available Agent Types

    ### general-purpose
    General-purpose agent for researching complex questions, searching for code, and executing multi-step tasks. When you are searching for a keyword or file and are not confident that you will find the right match in the first few tries use this agent to perform the search for you. (Tools: *)

    ## Usage Notes

    1. Each agent invocation is stateless. You will not be able to send additional messages to the agent, nor will the agent be able to communicate with you outside of its final report. Therefore, your prompt should contain a highly detailed task description for the agent to perform autonomously.
    2. The agent's outputs should generally be trusted
    3. Clearly tell the agent whether you expect it to write code or just to do research (search, file reads, web fetches, etc.), since it is not aware of the user's intent
    4. The result returned by the agent is the complete output from the agent execution

    Args:
        description: A short (3-5 word) description of the task
        prompt: The task for the agent to perform
        subagent_type: The type of specialized agent to use for this task (currently only "general-purpose" is supported)
    
    Returns:
        The agent's complete response after completing the task
    """
    # Validate subagent_type
    if subagent_type != "general-purpose":
        return f"Error: Unknown subagent_type '{subagent_type}'. Currently only 'general-purpose' is supported."
    
    try:
        # Create the specialized agent
        if subagent_type == "general-purpose":
            agent = create_general_purpose_agent()
        else:
            return f"Error: Unsupported agent type: {subagent_type}"
        
        # Execute the task
        result = agent.chat(prompt)
        
        # Return the complete result
        return f"Task completed: {description}\n\nAgent Response:\n{result}"
        
    except Exception as e:
        return f"Error executing task '{description}' with {subagent_type} agent: {str(e)}"