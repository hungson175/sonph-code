"""Dynamic agent implementation that loads from configuration."""

import re
from pathlib import Path
from typing import List, Dict, Set
from langchain_core.tools import BaseTool

from .base_agent import BaseAgent


class DynamicAgent(BaseAgent):
    """Agent created from user configuration that extends BaseAgent."""

    def __init__(
        self,
        system_prompt: str,
        tools: List[BaseTool] = None,
        model_name: str = "sonnet",
    ):
        """Initialize dynamic agent with BaseAgent functionality."""
        super().__init__(system_prompt, tools, model_name)

    @classmethod
    def from_config(cls, config: Dict):
        """Create agent from parsed config."""
        tools = cls._resolve_tools(config.get("tools", ["*"]))

        return cls(
            system_prompt=config.get("systemPrompt", ""),
            tools=tools,
            model_name=config.get("model", "sonnet"),
        )

    @staticmethod
    def _get_available_tools() -> Set[str]:
        """Scan coding_agent/tools directory to find all available tools.

        Returns:
            Set of tool names found in the tools directory
        """
        # Get tools directory relative to this file
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
        """Convert tool name strings to actual tool instances.

        Filters out non-existent tools from the list.
        """
        # Import all available tools
        from ..tools.file_tools import read_file, write_file, edit_file, list_files
        from ..tools.search_tools import glob_files, grep_files
        from ..tools.execution_tools import run_command, get_bash_output, todo_write
        from ..tools.task_tool import task_tool

        # Map tool names to actual tool objects
        available_tool_objects = {
            "Read": read_file,
            "Write": write_file,
            "Edit": edit_file,
            "MultiEdit": edit_file,  # assuming MultiEdit uses the same tool
            "LS": list_files,
            "Glob": glob_files,
            "Grep": grep_files,
            "Bash": run_command,
            "BashOutput": get_bash_output,
            "TodoWrite": todo_write,
            "Task": task_tool,
        }

        # If '*' is specified, return all available tools
        if tool_names == ["*"]:
            return list(available_tool_objects.values())

        # Get available tool names by scanning the tools directory
        available_tool_names = DynamicAgent._get_available_tools()

        # Filter and collect actual tool objects
        filtered_tools = []
        for tool_name in tool_names:
            if tool_name.startswith("mcp__"):
                # Skip MCP tools as they won't be implemented soon
                continue
            elif tool_name in available_tool_objects:
                filtered_tools.append(available_tool_objects[tool_name])
            elif tool_name in available_tool_names:
                # Tool exists but not in our mapping - warn but continue
                print(f"Warning: Tool '{tool_name}' found in codebase but not mapped")

        # Log filtered tools for debugging
        requested_non_mcp = [t for t in tool_names if not t.startswith("mcp__")]
        if len(filtered_tools) != len(requested_non_mcp):
            missing_tools = set(requested_non_mcp) - {
                tool.name for tool in filtered_tools
            }
            mcp_tools = {t for t in tool_names if t.startswith("mcp__")}
            if missing_tools:
                print(f"Warning: Filtered out non-existent tools: {missing_tools}")
            if mcp_tools:
                print(f"Info: Skipped MCP tools (not implemented): {mcp_tools}")

        # If no tools were resolved, fallback to default tools
        if not filtered_tools:
            print("Warning: No tools resolved, using default tool set")
            return None  # This will trigger BaseAgent to use default tools

        return filtered_tools
