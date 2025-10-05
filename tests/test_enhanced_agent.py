#!/usr/bin/env python3
"""
Test script to demonstrate the enhanced CLI with actual agent tool usage
Run with: python test_enhanced_agent.py
"""

import os
import sys
from coding_agent.core.agent import CodingAgent
from coding_agent.core.tool_wrapper import wrap_agent_tools, show_agent_phase
from coding_agent.ui.enhanced_cli import enhanced_cli
from rich.console import Console

console = Console()


def test_enhanced_agent():
    """Test the enhanced agent with visual feedback"""

    # Show startup
    console.print("[bold cyan]ENHANCED AGENT TEST[/bold cyan]")
    console.print("[yellow]Testing sonph-code with Rich UI enhancements[/yellow]\n")

    # Initialize agent info
    agent_count = {'total': 7, 'built_in': 1, 'user_defined': 6}
    enhanced_cli.show_startup_panel(os.getcwd(), agent_count)

    # Create agent
    show_agent_phase("INITIALIZATION", "Creating agent with Grok provider", "blue")
    agent = CodingAgent(provider_name="grok")

    # Wrap tools with enhanced display
    wrap_agent_tools(agent)

    # Test various operations
    test_cases = [
        {
            "phase": "FILE OPERATIONS",
            "description": "Testing file read and write operations",
            "style": "yellow",
            "task": "List all Python files in the current directory and count them"
        },
        {
            "phase": "CODE ANALYSIS",
            "description": "Searching for patterns in code",
            "style": "magenta",
            "task": "Search for all TODO comments in the codebase"
        },
        {
            "phase": "TASK MANAGEMENT",
            "description": "Creating and managing tasks",
            "style": "cyan",
            "task": "Create a todo list for implementing a new feature: user authentication with 3 subtasks"
        }
    ]

    for test in test_cases:
        # Show phase transition
        show_agent_phase(test["phase"], test["description"], test["style"])

        # Show the task
        enhanced_cli.show_status_message(f"Task: {test['task']}", "info")

        try:
            # Execute the task
            response = agent.chat(test["task"])

            # Show result
            if len(response) > 200:
                response_preview = response[:200] + "..."
            else:
                response_preview = response

            enhanced_cli.show_result_panel(
                "Task Completed",
                response_preview,
                "green"
            )

        except Exception as e:
            enhanced_cli.show_status_message(f"Task failed: {str(e)}", "error")

        # Separator between tests
        enhanced_cli.print_separator()

    # Final summary
    show_agent_phase("COMPLETE", "All tests finished", "green")
    enhanced_cli.show_status_message("Enhanced agent test completed successfully!", "complete")


def test_progress_during_execution():
    """Test progress indicators during actual tool execution"""

    console.print("\n[bold yellow]PROGRESS INDICATOR TEST[/bold yellow]")

    # Create agent
    agent = CodingAgent(provider_name="grok")
    wrap_agent_tools(agent)

    # Test with a longer operation
    show_agent_phase("LONG OPERATION", "Running analysis that takes time", "yellow")

    task = """
    Do the following steps:
    1. Count all Python files in the project
    2. Count all lines of code in those files
    3. Find the largest Python file
    """

    try:
        response = agent.chat(task)
        enhanced_cli.show_status_message("Analysis completed", "success")
    except Exception as e:
        enhanced_cli.show_status_message(f"Analysis failed: {str(e)}", "error")


def main():
    """Run all tests"""

    try:
        # Main test
        test_enhanced_agent()

        # Additional progress test
        test_progress_during_execution()

        # Show final success
        console.print("\n[bold green]✨ All enhanced CLI tests completed![/bold green]")

    except KeyboardInterrupt:
        enhanced_cli.show_status_message("Test interrupted by user", "warning")
        sys.exit(1)
    except Exception as e:
        enhanced_cli.show_status_message(f"Test failed: {str(e)}", "error")
        console.print_exception()
        sys.exit(1)


if __name__ == "__main__":
    main()