"""Task tool for delegating work to specialized agents."""

from langchain_core.tools import tool
from typing import Annotated


def create_general_purpose_agent():
    """Create a specialized research agent."""
    # Import here to avoid circular import
    from ..core.general_purpose_agent import GeneralPurposeAgent

    return GeneralPurposeAgent()


@tool("Task")
def task(
    description: Annotated[str, "A short (3-5 word) description of the task"],
    prompt: Annotated[str, "The task for the agent to perform"],
    subagent_type: Annotated[str, "The type of specialized agent to use for this task"],
) -> str:
    """Task tool with dynamic agent loading from registry.

    The actual description is set dynamically at application startup.
    """
    from ..core.agent_registry import AgentRegistry

    # Get the agent registry
    registry = AgentRegistry()

    try:
        # Load the specified agent
        agent = registry.load_agent(subagent_type)

        # Execute the task
        result = agent.chat(prompt)

        # Return the complete result
        return f"Task completed: {description}\n\nAgent Response:\n{result}"

    except Exception as e:
        # Get available agent types for error message
        available_agents = list(registry.get_available_agents().keys())
        return f"Error executing task '{description}' with {subagent_type} agent: {str(e)}\nAvailable agents: {available_agents}"


def initialize_task_tool_description():
    """Initialize the Task tool description at startup.

    This should be called once during application startup to set the
    static description for the Task tool based on available agents.
    """
    from ..core.task_tool_generator import get_static_task_description

    # Get the static description generated from available agents
    static_description = get_static_task_description()

    # Set the tool's docstring to the generated description
    task.__doc__ = static_description

    return static_description
