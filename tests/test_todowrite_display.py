#!/usr/bin/env python3
"""Test TodoWrite display with strikethrough for completed items"""

from coding_agent.core.agent import CodingAgent

# Create agent
agent = CodingAgent(provider_name="grok")

print("Testing TodoWrite display - completed items should be struck through")
print("=" * 70)

# Create a todo list with mixed statuses
todo_request = """
Create a todo list with these items:
1. Setup development environment (completed)
2. Install dependencies (completed)
3. Configure database (in progress)
4. Write unit tests (pending)
5. Deploy to production (pending)
"""

response = agent.chat(todo_request)

print("\n" + "=" * 70)
print("The todo list above should show:")
print("- Completed items (#1, #2) with strikethrough text")
print("- In progress item (#3) with 🔄 icon")
print("- Pending items (#4, #5) with ⏳ icon")
print("- NO activeForm text shown")