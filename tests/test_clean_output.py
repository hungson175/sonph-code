#!/usr/bin/env python3
"""Test that the output is now clean without debug info"""

from coding_agent.core.agent import CodingAgent

# Create agent
agent = CodingAgent(provider_name="grok")

print("Testing clean output - no verbose debug info should appear")
print("=" * 60)

# Simple test that triggers tool use
response = agent.chat("List files in the current directory")

print("\n" + "=" * 60)
print("Test completed. Output should be clean and professional!")