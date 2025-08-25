"""Generate STATIC Task tool description at startup.

IMPORTANT: This module should only be called ONCE during application startup
to generate a STATIC Task tool description. The description must be frozen
for the entire application lifetime due to LLM caching requirements.
"""

from typing import Annotated
from agent_registry import AgentRegistry


def generate_static_task_description() -> str:
    """Generate STATIC Task tool description with all available agents.

    This function should ONLY be called during application startup.
    The resulting description must be frozen for the entire application lifetime.

    Returns:
        str: Static Task tool description including all available agents
    """
    registry = AgentRegistry()
    agent_lines = registry.get_agent_list_for_task_tool()

    base_description = "Launch a new agent to handle complex, multi-step tasks autonomously.\n\nAvailable agent types and the tools they have access to:"

    usage_notes = """
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
    str: The agent's complete response after completing the task"""

    return base_description + "\n" + "\n".join(agent_lines) + usage_notes


# For backward compatibility - deprecated
def generate_task_description() -> str:
    """DEPRECATED: Use generate_static_task_description() instead."""
    print(
        "WARNING: generate_task_description() is deprecated. Use generate_static_task_description() at startup only."
    )
    return generate_static_task_description()


def create_mock_task_tool():
    """Create a mock Task tool for testing (not the real LangChain tool)."""

    def task(
        description: Annotated[str, "A short (3-5 word) description of the task"],
        prompt: Annotated[str, "The task for the agent to perform"],
        subagent_type: Annotated[
            str, "The type of specialized agent to use for this task"
        ],
    ) -> str:
        registry = AgentRegistry()

        try:
            agent = registry.load_agent(subagent_type)
            result = agent.chat(prompt)
            return f"Task completed: {description}\n\nAgent Response:\n{result}"
        except Exception as e:
            return f"Error executing task '{description}' with {subagent_type} agent: {str(e)}"

    # Set the STATIC description (should only be called at startup)
    task.__doc__ = generate_static_task_description()
    return task


if __name__ == "__main__":
    # Test the Task tool generation
    print("🔧 Testing Task Tool Generation")
    print("=" * 60)

    registry = AgentRegistry()
    counts = registry.get_agent_count()
    print(
        f"📊 Agent Count: {counts['total']} total ({counts['built_in']} built-in, {counts['user_defined']} user-defined)"
    )

    description = generate_static_task_description()
    print(f"📝 Generated description length: {len(description)} characters")
    print()

    print("📋 Task Tool Description (first 1000 chars):")
    print("-" * 60)
    print(description[:1000])
    print("...")
    print("-" * 60)

    # Test the mock tool
    print("\n🧪 Testing Mock Task Tool")
    task_tool = create_mock_task_tool()

    try:
        result = task_tool(
            "UI analysis", "Review the dashboard design", "ui-ux-designer"
        )
        print(f"✅ Test successful: {result[:100]}...")
    except Exception as e:
        print(f"❌ Test failed: {e}")

    try:
        result = task_tool("Invalid test", "Test invalid agent", "nonexistent-agent")
        print(f"✅ Error handling: {result[:100]}...")
    except Exception as e:
        print(f"❌ Error handling failed: {e}")
