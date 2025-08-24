"""Task tool for delegating work to specialized agents."""

from langchain_core.tools import tool
from typing import Dict, Any


def create_general_purpose_agent():
    """Create a specialized research agent."""
    # Import here to avoid circular import
    from ..core.general_purpose_agent import GeneralPurposeAgent
    
    return GeneralPurposeAgent()


@tool("Task")
def task(description: str, prompt: str, subagent_type: str) -> str:
    """Launch a new agent to handle complex, multi-step tasks autonomously. 

Available agent types and the tools they have access to:
- general-purpose: General-purpose agent for researching complex questions, searching for code, and executing multi-step tasks. When you are searching for a keyword or file and are not confident that you will find the right match in the first few tries use this agent to perform the search for you. (Tools: *)

When using the Task tool, you must specify a subagent_type parameter to select which agent type to use.



When NOT to use the Agent tool:
- If you want to read a specific file path, use the Read or Glob tool instead of the Agent tool, to find the match more quickly
- If you are searching for a specific class definition like "class Foo", use the Glob tool instead, to find the match more quickly
- If you are searching for code within a specific file or set of 2-3 files, use the Read tool instead of the Agent tool, to find the match more quickly
- Other tasks that are not related to the agent descriptions above


Usage notes:
1. Launch multiple agents concurrently whenever possible, to maximize performance; to do that, use a single message with multiple tool uses
2. When the agent is done, it will return a single message back to you. The result returned by the agent is not visible to the user. To show the user the result, you should send a text message back to the user with a concise summary of the result.
3. Each agent invocation is stateless. You will not be able to send additional messages to the agent, nor will the agent be able to communicate with you outside of its final report. Therefore, your prompt should contain a highly detailed task description for the agent to perform autonomously and you should specify exactly what information the agent should return back to you in its final and only message to you.
4. The agent's outputs should generally be trusted
5. Clearly tell the agent whether you expect it to write code or just to do research (search, file reads, web fetches, etc.), since it is not aware of the user's intent
6. If the agent description mentions that it should be used proactively, then you should try your best to use it without the user having to ask for it first. Use your judgement.

    Args:
        description: A short (3-5 word) description of the task
        prompt: The task for the agent to perform
        subagent_type: The type of specialized agent to use for this task
    
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