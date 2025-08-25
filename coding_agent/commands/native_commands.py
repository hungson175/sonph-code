"""Native built-in commands for the coding agent."""


class InitCommand:
    """Built-in /init command for analyzing codebase and creating CLAUDE.md"""

    @staticmethod
    def get_init_prompt() -> str:
        """Get the init command prompt."""
        return """Please analyze this codebase and create a CLAUDE.md file, which will be given to future instances of Claude Code to operate in this repository.
            
What to add:
1. Commands that will be commonly used, such as how to build, lint, and run tests. Include the necessary commands to develop in this codebase, such as how to run a single test.
2. High-level code architecture and structure so that future instances can be productive more quickly. Focus on the "big picture" architecture that requires reading multiple files to understand

Usage notes:
- If there's already a CLAUDE.md, suggest improvements to it.
- When you make the initial CLAUDE.md, do not repeat yourself and do not include obvious instructions like "Provide helpful error messages to users", "Write unit tests for all new utilities", "Never include sensitive information (API keys, tokens) in code or commits" 
- Avoid listing every component or file structure that can be easily discovered
- Don't include generic development practices
- If there are Cursor rules (in .cursor/rules/ or .cursorrules) or Copilot rules (in .github/copilot-instructions.md), make sure to include the important parts.
- If there is a README.md, make sure to include the important parts. 
- Do not make up information such as "Common Development Tasks", "Tips for Development", "Support and Documentation" unless this is expressly included in other files that you read.
- Be sure to prefix the file with the following text:

```
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
```"""

    @staticmethod
    def process() -> str:
        """Process the /init command."""
        init_prompt = InitCommand.get_init_prompt()

        return f"""<command-message>init is analyzing your codebase…</command-message>
<command-name>/init</command-name>

{init_prompt}"""


class NativeCommandManager:
    """Manages built-in native commands."""

    def __init__(self):
        self.native_commands = {"init": InitCommand()}

    def is_native_command(self, command_name: str) -> bool:
        """Check if a command is a native command."""
        return command_name in self.native_commands

    def process_native_command(self, command_name: str, _arguments: str = "") -> str:
        """Process a native command."""
        if command_name == "init":
            return InitCommand.process()

        return f"Unknown native command: {command_name}"

    def list_native_commands(self) -> list:
        """List all native commands."""
        return list(self.native_commands.keys())
