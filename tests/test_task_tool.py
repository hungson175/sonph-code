#!/usr/bin/env python3
"""Test script for the Task tool."""

from coding_agent.core.agent import CodingAgent


def test_task_tool():
    """Test the Task tool with a simple example."""
    print("🧪 Testing Task tool implementation...")

    # Create agent
    agent = CodingAgent()

    # Test the Task tool with a simple research task
    test_prompt = 'Use the Task tool to search for all Python files in this project and give me a summary of what each file does. Use description="analyze python files" and subagent_type="general-purpose".'

    print(f"\n📝 Test prompt: {test_prompt}")

    try:
        result = agent.chat(test_prompt)
        print(f"\n✅ Result: {result}")
        return True
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False


if __name__ == "__main__":
    success = test_task_tool()
    exit(0 if success else 1)
