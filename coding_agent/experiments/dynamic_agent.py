"""Dynamic agent implementation that loads from configuration."""

import re
from pathlib import Path
from typing import List, Dict, Set
from langchain_core.tools import BaseTool


class DynamicAgent:
    """Agent created from user configuration.

    This is a simplified version for testing. In production, this would
    inherit from BaseAgent and have full agent capabilities.
    """

    def __init__(
        self, system_prompt: str, tools: List[BaseTool], model_name: str = "sonnet"
    ):
        """Initialize dynamic agent."""
        self.system_prompt = system_prompt
        self.tools = tools
        self.model_name = model_name

    @classmethod
    def from_config(cls, config: Dict, model_name: str = None):
        """Create agent from parsed config."""
        tools = cls._resolve_tools(config.get("tools", ["*"]))

        return cls(
            system_prompt=config.get("systemPrompt", ""),
            tools=tools,
            model_name=model_name or config.get("model", "sonnet"),
        )

    @staticmethod
    def _get_available_tools() -> Set[str]:
        """Scan coding_agent/tools directory to find all available tools.

        Returns:
            Set of tool names found in the tools directory
        """
        tools_dir = Path(__file__).parent.parent / "tools"
        available_tools = set()

        if not tools_dir.exists():
            print(f"Warning: Tools directory not found: {tools_dir}")
            return available_tools

        # Scan all Python files in tools directory
        for py_file in tools_dir.glob("*.py"):
            if py_file.name.startswith("__"):
                continue

            try:
                content = py_file.read_text(encoding="utf-8")
                # Find @tool("ToolName") patterns
                tool_matches = re.findall(r'@tool\(["\']([^"\']+)["\']\)', content)
                available_tools.update(tool_matches)
            except Exception as e:
                print(f"Warning: Failed to read {py_file}: {e}")

        return available_tools

    @staticmethod
    def _resolve_tools(tool_names: List[str]) -> List[BaseTool]:
        """Convert tool name strings to tool instances.

        Filters out non-existent tools from the list.
        This is a simplified version for testing. In production, this would
        import and return actual tool instances.
        """
        if tool_names == ["*"]:
            return ["all_tools_placeholder"]

        # Get available tools by scanning the tools directory
        available_tools = DynamicAgent._get_available_tools()

        # Filter out non-existent tools and MCP tools
        filtered_tools = []
        for tool in tool_names:
            if tool.startswith("mcp__"):
                # Skip MCP tools as they won't be implemented soon
                continue
            elif tool in available_tools:
                filtered_tools.append(tool)

        # Log filtered tools for debugging
        if len(filtered_tools) != len(tool_names):
            missing_tools = (
                set(tool_names)
                - set(filtered_tools)
                - {t for t in tool_names if t.startswith("mcp__")}
            )
            mcp_tools = {t for t in tool_names if t.startswith("mcp__")}
            if missing_tools:
                print(f"Warning: Filtered out non-existent tools: {missing_tools}")
            if mcp_tools:
                print(f"Info: Skipped MCP tools (not implemented): {mcp_tools}")

        return filtered_tools

    def chat(self, user_input: str) -> str:
        """Process user request.

        This is a mock implementation for testing. In production, this would
        use the actual LLM and tools.
        """
        return f"[DynamicAgent] Processed request with {len(self.tools)} tools using {self.model_name}: {user_input[:50]}..."
