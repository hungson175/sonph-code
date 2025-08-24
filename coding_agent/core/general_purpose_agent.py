"""General purpose agent for research and analysis tasks."""

from langchain_core.messages import HumanMessage
from langchain_core.tools import BaseTool
from typing import List

from .base_agent import BaseAgent
from .config import Config
from ..utils.context import load_memory_context
from ..tools.file_tools import read_file, write_file, edit_file, list_files
from ..tools.search_tools import glob_files, grep_files
from ..tools.execution_tools import run_command, get_bash_output, todo_write


class GeneralPurposeAgent(BaseAgent):
    """Agent specialized in research and analysis tasks."""
    
    def __init__(self, model_name: str = Config.MODEL_NAME):
        """Initialize general purpose agent."""
        # Load memory context (same as CodingAgent needs)
        self.memory_context = load_memory_context()
        
        super().__init__(
            system_prompt=self._get_general_purpose_prompt(),
            tools=self._get_research_tools(),  # No Task tool to avoid recursion
            model_name=model_name
        )
        
        # Add memory context if exists (same pattern as CodingAgent)
        if self.memory_context and len(self.memory_context.strip()) > 100:
            self.messages.append(
                HumanMessage(content=self._create_cached_message(self.memory_context))
            )
    
    def _get_general_purpose_prompt(self) -> str:
        """Get the general purpose agent system prompt."""
        return """You are an agent for Claude Code, Anthropic's official CLI for Claude. Given the user's message, you should use the tools available to complete the task. Do what has been asked; nothing more, nothing less. When you complete the task simply respond with a detailed writeup.

Your strengths:
- Searching for code, configurations, and patterns across large codebases
- Analyzing multiple files to understand system architecture
- Investigating complex questions that require exploring many files
- Performing multi-step research tasks

Guidelines:
- For file searches: Use Grep or Glob when you need to search broadly. Use Read when you know the specific file path.
- For analysis: Start broad and narrow down. Use multiple search strategies if the first doesn't yield results.
- Be thorough: Check multiple locations, consider different naming conventions, look for related files.
- NEVER create files unless they're absolutely necessary for achieving your goal. ALWAYS prefer editing an existing file to creating a new one.
- NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested.
- In your final response always share relevant file names and code snippets. Any file paths you return in your response MUST be absolute. Do NOT use relative paths.
- For clear communication, avoid using emojis."""
    
    def _get_research_tools(self) -> List[BaseTool]:
        """Get research tools (excludes Task tool to prevent infinite recursion)."""
        return [
            read_file,
            write_file, 
            edit_file,
            run_command,
            list_files,
            glob_files,
            grep_files,
            get_bash_output,
            todo_write
        ]