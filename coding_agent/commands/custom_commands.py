"""Custom command management."""

import time
from pathlib import Path
from typing import Dict, List, Optional

from colorama import Fore

from ..core.config import Config


class CustomCommand:
    """Represents a single custom command."""

    def __init__(self, name: str, template: str):
        self.name = name
        self.template = template

    def process(self, arguments: str = "") -> str:
        """Process command with arguments."""
        processed_template = self.template.replace("$ARGUMENTS", arguments)

        return f"""<command-message>Executing custom command: /{self.name}</command-message>
<command-name>/{self.name}</command-name>
<command-arguments>{arguments}</command-arguments>

{processed_template}"""


class CustomCommandManager:
    """Manages custom commands from ~/.claude/commands directory."""

    def __init__(self):
        self.commands_dir = Path.home() / ".claude" / "commands"
        self.commands_cache: Dict[str, CustomCommand] = {}
        self.last_scan_time = 0
        self.cache_duration = Config.CACHE_DURATION_SECONDS

    def _scan_commands(self) -> None:
        """Scan the commands directory and cache command templates."""
        if not self.commands_dir.exists():
            return

        current_time = time.time()
        if (
            current_time - self.last_scan_time < self.cache_duration
            and self.commands_cache
        ):
            return  # Use cached commands

        self.commands_cache.clear()

        try:
            for command_file in self.commands_dir.glob("*.md"):
                command_name = command_file.stem
                try:
                    with open(command_file, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                    self.commands_cache[command_name] = CustomCommand(
                        command_name, content
                    )
                except Exception as e:
                    print(f"{Fore.YELLOW}⚠️  Could not load command {command_name}: {e}")

            self.last_scan_time = current_time

        except Exception as e:
            print(f"{Fore.YELLOW}⚠️  Could not scan commands directory: {e}")

    def get_command(self, command_name: str) -> Optional[CustomCommand]:
        """Get a command by name."""
        self._scan_commands()
        return self.commands_cache.get(command_name)

    def list_commands(self) -> List[str]:
        """List all available custom commands."""
        self._scan_commands()
        return list(self.commands_cache.keys())
