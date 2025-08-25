#!/usr/bin/env python3
"""Comprehensive test of the dynamic agent system."""

import sys
from pathlib import Path
from agent_registry import AgentRegistry
from agent_config_parser import AgentConfigParser
from task_tool_generator import generate_static_task_description, create_mock_task_tool


def test_parser():
    """Test the agent configuration parser."""
    print("🔍 Testing Agent Configuration Parser")
    print("-" * 50)

    agent_dir = Path.home() / ".claude" / "agents"
    if not agent_dir.exists():
        print(f"❌ Agent directory does not exist: {agent_dir}")
        return False

    parser = AgentConfigParser()
    success_count = 0
    total_count = 0

    for md_file in agent_dir.glob("*.md"):
        total_count += 1
        print(f"📄 {md_file.name}: ", end="")

        try:
            config = parser.parse_agent_md(md_file)
            print(f"✅ {config['agentType']} ({len(config['systemPrompt'])} chars)")
            success_count += 1
        except Exception as e:
            print(f"❌ {e}")

    print(
        f"\n📊 Parser Results: {success_count}/{total_count} files parsed successfully"
    )
    return success_count == total_count


def test_registry():
    """Test the agent registry."""
    print("\n🗂️  Testing Agent Registry")
    print("-" * 50)

    registry = AgentRegistry()

    # Test agent discovery
    agents = registry.get_available_agents()
    counts = registry.get_agent_count()

    print(f"📊 Discovered {counts['total']} agents:")
    print(f"   - Built-in: {counts['built_in']}")
    print(f"   - User-defined: {counts['user_defined']}")
    print()

    # List all agents
    for agent_type, config in agents.items():
        source = config["source"]
        tools = config["tools"]
        tools_str = f"{len(tools)} tools" if tools != ["*"] else "all tools"
        print(f"  📋 {agent_type} ({source}) - {tools_str}")

    # Test agent loading
    print("\n🚀 Testing Agent Loading:")
    success_count = 0

    for agent_type in agents.keys():
        try:
            agent = registry.load_agent(agent_type)
            print(f"  ✅ {agent_type}: Loaded successfully")
            success_count += 1
        except Exception as e:
            print(f"  ❌ {agent_type}: {e}")

    print(
        f"\n📊 Loading Results: {success_count}/{len(agents)} agents loaded successfully"
    )
    return success_count == len(agents)


def test_task_tool_generation():
    """Test Task tool description generation."""
    print("\n🔧 Testing Task Tool Generation")
    print("-" * 50)

    try:
        description = generate_static_task_description()
        print(f"✅ Generated description: {len(description)} characters")

        # Check that all agents are included
        registry = AgentRegistry()
        agents = registry.get_available_agents()

        missing_agents = []
        for agent_type in agents.keys():
            if agent_type not in description:
                missing_agents.append(agent_type)

        if missing_agents:
            print(f"⚠️  Missing agents in description: {missing_agents}")
            return False
        else:
            print(f"✅ All {len(agents)} agents included in description")

        return True

    except Exception as e:
        print(f"❌ Task tool generation failed: {e}")
        return False


def test_mock_task_execution():
    """Test mock task execution."""
    print("\n🧪 Testing Mock Task Execution")
    print("-" * 50)

    task_tool = create_mock_task_tool()

    # Test valid agent
    try:
        result = task_tool(
            description="Design review",
            prompt="Please review the user interface design for our dashboard",
            subagent_type="ui-ux-designer",
        )
        print("✅ Valid agent execution:")
        print(f"   {result[:100]}...")
    except Exception as e:
        print(f"❌ Valid agent execution failed: {e}")
        return False

    # Test invalid agent
    try:
        result = task_tool(
            description="Invalid test",
            prompt="This should fail",
            subagent_type="nonexistent-agent",
        )
        if "Error executing task" in result:
            print("✅ Invalid agent error handling:")
            print(f"   {result[:100]}...")
        else:
            print(f"⚠️  Expected error but got: {result[:50]}...")
            return False
    except Exception as e:
        print(f"❌ Error handling failed: {e}")
        return False

    return True


def main():
    """Run all tests."""
    print("🧪 Dynamic Agent System - Comprehensive Test")
    print("=" * 60)

    tests = [
        ("Parser", test_parser),
        ("Registry", test_registry),
        ("Task Tool Generation", test_task_tool_generation),
        ("Mock Task Execution", test_mock_task_execution),
    ]

    results = []

    for test_name, test_func in tests:
        success = test_func()
        results.append((test_name, success))

    # Summary
    print("\n📊 Test Summary")
    print("=" * 60)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")

    print(f"\n🎯 Overall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! The dynamic agent system is working correctly.")
        return 0
    else:
        print("💥 Some tests failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
