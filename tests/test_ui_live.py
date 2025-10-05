#!/usr/bin/env python3
"""Test the enhanced UI with a simple agent task"""

from coding_agent.core.agent import CodingAgent
from coding_agent.ui.enhanced_cli import enhanced_cli

# Show startup
enhanced_cli.show_startup_panel("/tmp", {'total': 7, 'built_in': 1, 'user_defined': 6})

# Create agent
agent = CodingAgent(provider_name="grok")

# Test a simple command that will trigger tool usage
enhanced_cli.show_phase_transition("TESTING ENHANCED UI", "Running LS tool to test display", "cyan")

response = agent.chat("List files in /tmp directory")

print("\n" + "=" * 60)
print("Response:", response[:200])
print("=" * 60)

enhanced_cli.show_status_message("Test completed!", "complete")