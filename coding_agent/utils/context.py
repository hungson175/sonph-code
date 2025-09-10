"""Context and memory management utilities."""

from pathlib import Path


def load_memory_context(working_dir: str = None) -> str:
    """Load memory context from global and project CLAUDE.md files.
    
    Args:
        working_dir: The working directory to load project CLAUDE.md from.
                    If None, uses current directory.
    """
    context_parts = []

    # Try to load global CLAUDE.md from ~/.claude/CLAUDE.md
    global_claude_path = Path.home() / ".claude" / "CLAUDE.md"
    
    # Use working directory if provided, otherwise current directory
    if working_dir:
        project_claude_path = Path(working_dir) / "CLAUDE.md"
    else:
        project_claude_path = Path(".") / "CLAUDE.md"

    context_parts.append("<system-reminder>")
    context_parts.append(
        "As you answer the user's questions, you can use the following context:"
    )
    context_parts.append("# claudeMd")
    context_parts.append(
        "Codebase and user instructions are shown below. Be sure to adhere to these instructions. IMPORTANT: These instructions OVERRIDE any default behavior and you MUST follow them exactly as written."
    )
    context_parts.append("")

    # Load global instructions if they exist
    if global_claude_path.exists():
        try:
            with open(global_claude_path, "r", encoding="utf-8") as f:
                global_content = f.read().strip()
            context_parts.append(
                f"Contents of {global_claude_path} (user's private global instructions for all projects):"
            )
            context_parts.append("")
            context_parts.append(global_content)
            context_parts.append("")
        except Exception as e:
            from colorama import Fore

            print(f"{Fore.YELLOW}⚠️  Could not load global CLAUDE.md: {e}")

    # Load project instructions if they exist
    if project_claude_path.exists():
        try:
            with open(project_claude_path, "r", encoding="utf-8") as f:
                project_content = f.read().strip()
            context_parts.append(
                f"Contents of {project_claude_path.resolve()} (project instructions, checked into the codebase):"
            )
            context_parts.append("")
            context_parts.append(project_content)
            context_parts.append("")
        except Exception as e:
            from colorama import Fore

            print(f"{Fore.YELLOW}⚠️  Could not load project CLAUDE.md: {e}")

    context_parts.append("      ")
    context_parts.append(
        "      IMPORTANT: this context may or may not be relevant to your tasks. You should not respond to this context unless it is highly relevant to your task."
    )
    context_parts.append("</system-reminder>")

    return "\n".join(context_parts)
