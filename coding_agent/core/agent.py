"""Main CodingAgent class."""

from langchain_core.messages import HumanMessage, ToolMessage
from colorama import Fore, Style

from .base_agent import BaseAgent
from .config import Config
from .prompts import coding_agent_prompt
from ..commands.custom_commands import CustomCommandManager
from ..commands.native_commands import NativeCommandManager
from ..utils.context import load_memory_context
from ..tools.file_tools import read_file, write_file, edit_file, list_files
from ..tools.search_tools import glob_files, grep_files
from ..tools.execution_tools import run_command, get_bash_output, todo_write
from ..tools.task_tool import task


class CodingAgent(BaseAgent):
    def __init__(self, model_name: str = Config.MODEL_NAME):
        """Initialize the coding agent with tools and caching."""
        # Initialize command managers
        self.command_manager = CustomCommandManager()
        self.native_command_manager = NativeCommandManager()
        
        # Load memory context
        self.memory_context = load_memory_context()
        
        # Call parent with coding-specific configuration
        super().__init__(
            system_prompt=coding_agent_prompt(),
            tools=self._get_coding_tools(),
            model_name=model_name
        )
        
        # Add memory context if exists
        if self.memory_context and len(self.memory_context.strip()) > 100:
            self.messages.append(
                HumanMessage(content=self._create_cached_message(self.memory_context))
            )

    def _get_coding_tools(self):
        """Get tools specific to coding agent (includes Task tool)."""
        return [
            read_file,
            write_file,
            edit_file,
            run_command,
            list_files,
            glob_files,
            grep_files,
            get_bash_output,
            todo_write,
            task,
        ]



