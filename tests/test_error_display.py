#!/usr/bin/env python3
"""Test that errors are displayed correctly"""

from coding_agent.core.agent import CodingAgent
from coding_agent.ui.enhanced_cli import enhanced_cli

# Create agent
agent = CodingAgent(provider_name="grok")

print("TEST 1: Normal file read (should show green checkmark)")
print("=" * 60)
response = agent.chat("Read the first 5 lines of /Users/sonph36/dev/demo/sonph-code/README.md")
print()

print("TEST 2: File that doesn't exist (should show red X)")
print("=" * 60)
response = agent.chat("Read the file /this/file/does/not/exist.txt")
print()

print("TEST 3: Search for 'error' in files (should show green, not red)")
print("=" * 60)
response = agent.chat("Search for the word 'error' in the current directory")
print()

enhanced_cli.show_status_message("All tests completed!", "complete")