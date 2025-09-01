"""Task tool for delegating work to specialized agents."""

from langchain_core.tools import StructuredTool


def create_general_purpose_agent():
    """Create a specialized research agent."""
    # Import here to avoid circular import
    from ..core.general_purpose_agent import GeneralPurposeAgent

    return GeneralPurposeAgent()


def _task_implementation(description: str, prompt: str, subagent_type: str) -> str:
    """Implementation function for the task tool."""
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


# Create the tool with a placeholder description that will be updated
task = StructuredTool.from_function(
    func=_task_implementation,
    name="Task",
    description="Task tool with dynamic agent loading from registry. The actual description is set dynamically at application startup.",
    args_schema=None,  # Will infer from function signature
)


def initialize_task_tool_description():
    """Initialize the Task tool description at startup.

    This should be called once during application startup to set the
    static description for the Task tool based on available agents.
    """
    from ..core.task_tool_generator import get_static_task_description

    # Get the static description generated from available agents
    static_description = get_static_task_description()

    # Update the tool's description directly
    task.description = static_description

    return static_description
