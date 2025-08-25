"""Base agent class for configurable agents."""

from typing import List
from langchain_anthropic import ChatAnthropic, convert_to_anthropic_tool
from langchain_core.messages import SystemMessage
from langchain_core.tools import BaseTool

from .config import Config
from ..utils.keyboard import setup_keyboard_interrupt


class BaseAgent:
    """Configurable agent base class."""

    def __init__(
        self,
        system_prompt: str,
        tools: List[BaseTool] = None,
        model_name: str = Config.MODEL_NAME,
    ):
        """Initialize agent with configurable system prompt and tools."""
        # Setup keyboard interrupt handling
        setup_keyboard_interrupt()

        # Store configuration
        self.system_prompt_str = system_prompt
        self.working_dir = "."

        # Setup LLM
        self.llm = ChatAnthropic(model=model_name, temperature=0.0, max_tokens=16384)

        # Setup tools AFTER prompt is set
        self.tools = tools or self._get_default_tools()
        self.tools_map, self.llm_with_tools = self._setup_tools()

        # Initialize with correct prompt from the start
        self.messages = [
            SystemMessage(content=self._create_cached_message(system_prompt))
        ]

    def _get_default_tools(self) -> List[BaseTool]:
        """Get default tool set - override in subclasses."""
        from ..tools.file_tools import read_file, write_file, edit_file, list_files
        from ..tools.search_tools import glob_files, grep_files
        from ..tools.execution_tools import run_command, get_bash_output, todo_write

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
        ]

    def _setup_tools(self):
        """Setup tools with caching and create tools map."""
        tools_map = {tool.name: tool for tool in self.tools}

        # Convert tools with caching on LAST tool only
        cached_tools = []
        for i, tool_obj in enumerate(self.tools):
            anthropic_tool = convert_to_anthropic_tool(tool_obj)
            if i == len(self.tools) - 1:
                anthropic_tool["cache_control"] = {"type": "ephemeral"}
            cached_tools.append(anthropic_tool)

        # Bind tools to LLM
        llm_with_tools = self.llm.bind_tools(cached_tools)

        return tools_map, llm_with_tools

    def _create_cached_message(self, content: str):
        """Create a message with cache control."""
        return [
            {"type": "text", "text": content, "cache_control": {"type": "ephemeral"}}
        ]

    def _remove_cache_control(self, message):
        """Remove cache control from message for reuse."""
        if hasattr(message, "content") and isinstance(message.content, list):
            if len(message.content) > 0 and isinstance(message.content[0], dict):
                message.content[0].pop("cache_control", None)

    def set_working_dir(self, directory: str):
        """Set the working directory for commands."""
        from colorama import Fore

        self.working_dir = directory
        print(Fore.GREEN + f"📁 Working directory set to: {directory}")

    def chat(self, user_input: str) -> str:
        """Process user request."""
        from langchain_core.messages import HumanMessage, ToolMessage
        from colorama import Fore, Style

        # Add user message with cache control
        self.messages.append(
            HumanMessage(content=self._create_cached_message(user_input))
        )

        # Get initial response
        response = self.llm_with_tools.invoke(self.messages)

        print(Fore.CYAN + "=" * 50)
        print(Fore.GREEN + "🤖 Initial response: " + Style.RESET_ALL, response)

        print(Fore.YELLOW + "=" * 20)
        usage = response.response_metadata.get("usage", {})
        print(
            Fore.BLUE + f"📊 Tokens - Input: {usage.get('input_tokens', 0)} "
            f"(cached: {usage.get('cache_read_input_tokens', 0)}) "
            f"Output: {usage.get('output_tokens', 0)}"
        )
        print(Fore.YELLOW + "=" * 20)

        # Remove cache_control from user message
        self._remove_cache_control(self.messages[-1])

        # Add response
        self.messages.append(response)

        # Handle tool calls
        while hasattr(response, "tool_calls") and response.tool_calls:
            print(
                Fore.MAGENTA + f"\n🔧 Executing {len(response.tool_calls)} tool(s)..."
            )

            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]

                # Special handling for run_command to use working_dir
                if tool_name == "run_command" and "working_dir" not in tool_args:
                    tool_args["working_dir"] = self.working_dir

                print(Fore.CYAN + "\n🔧 TOOL CALL DEBUG:")
                print(Fore.WHITE + f"   📝 Name: {tool_name}")
                print(Fore.WHITE + f"   ⚙️  Parameters: {tool_args}")

                # Show cancellation instruction for potentially long-running tools
                if tool_name in ["run_command", "grep_files"]:
                    print(Fore.YELLOW + "   ⌨️  Press Ctrl+C to cancel if needed")

                # Execute tool
                if tool_name in self.tools_map:
                    tool_result = self.tools_map[tool_name].invoke(tool_args)
                else:
                    tool_result = f"Unknown tool: {tool_name}"

                print(
                    Fore.GREEN
                    + f"   ✅ Result (first 500 chars): {str(tool_result)[:500]}..."
                )
                print(
                    Fore.BLUE
                    + f"   📏 Result length: {len(str(tool_result))} characters"
                )
                print(Fore.CYAN + "=" * 50)

                # Add tool result
                self.messages.append(
                    ToolMessage(
                        content=str(tool_result)[:5000],  # Limit size
                        tool_call_id=tool_call["id"],
                    )
                )

            # add cache_control
            last_message = self.messages[-1]
            self.messages[-1].content = self._create_cached_message(
                last_message.content
            )
            response = self.llm_with_tools.invoke(self.messages)
            # remove cache_control mark for reuse later on
            self._remove_cache_control(self.messages[-1])

            self.messages.append(response)
            usage = response.response_metadata.get("usage", {})
            print(
                Fore.BLUE + f"📊 After tools - Input: {usage.get('input_tokens', 0)} "
                f"(cached: {usage.get('cache_read_input_tokens', 0)})"
            )

        return response.content

    def reset(self):
        """Reset conversation but keep cached system prompt and memory context."""
        from colorama import Fore

        if len(self.messages) >= 2 and "<system-reminder>" in str(
            self.messages[1].content
        ):
            # Keep system prompt and memory context
            self.messages = [self.messages[0], self.messages[1]]
            print(
                Fore.YELLOW
                + "🔄 Conversation reset (keeping cached system prompt and memory context)"
            )
        else:
            # Only keep system prompt
            self.messages = [self.messages[0]]
            print(Fore.YELLOW + "🔄 Conversation reset (keeping cached system prompt)")
