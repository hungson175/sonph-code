"""Agent configuration parser for .md files with YAML frontmatter."""

import yaml
from pathlib import Path
from typing import Dict
from .config import Config


class AgentConfigParser:
    """Parse agent configuration from .md files with YAML frontmatter."""

    @staticmethod
    def parse_agent_md(file_path: Path) -> Dict:
        """Parse agent .md file into config dict.

        Expected format:
        ---
        name: agent-name
        description: When to use this agent...
        tools: Tool1, Tool2, Tool3  (optional, defaults to *)
        model: claude-sonnet-4-20250514 (optional)
        color: blue (optional)
        ---

        System prompt content here...

        Args:
            file_path: Path to .md file

        Returns:
            Dict with keys: agentType, whenToUse, systemPrompt, tools, model, color, source, baseDir, configFile
        """
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Split frontmatter and content
        if not content.startswith("---"):
            raise ValueError(f"File {file_path} does not start with YAML frontmatter")

        # Find the end of frontmatter
        parts = content.split("---", 2)
        if len(parts) < 3:
            raise ValueError(f"File {file_path} missing closing --- for frontmatter")

        # Parse YAML frontmatter
        frontmatter_yaml = parts[1].strip()
        system_prompt = parts[2].strip()

        try:
            # Use safe_load with improved YAML handling for multi-line strings
            frontmatter = yaml.safe_load(frontmatter_yaml)
        except yaml.YAMLError:
            # If YAML parsing fails, try fallback parsing for simple key-value pairs
            frontmatter = AgentConfigParser._parse_simple_frontmatter(frontmatter_yaml)

        # Build config dict
        config = {}

        # Required fields
        config["agentType"] = frontmatter.get("name")
        config["whenToUse"] = frontmatter.get("description", "")
        config["systemPrompt"] = system_prompt

        # Optional fields
        tools_str = frontmatter.get("tools", "*")
        if isinstance(tools_str, str):
            if tools_str.strip() == "*":
                config["tools"] = ["*"]
            else:
                # Split comma-separated tools and clean them up
                config["tools"] = [
                    tool.strip() for tool in tools_str.split(",") if tool.strip()
                ]
        else:
            config["tools"] = tools_str or ["*"]

        config["model"] = frontmatter.get("model", Config.MODEL_NAME)
        config["color"] = frontmatter.get("color", None)

        # Add metadata
        config["source"] = "user-defined"
        config["baseDir"] = str(file_path.parent)
        config["configFile"] = str(file_path)

        # Validation
        if not config["agentType"]:
            raise ValueError(f"Missing 'name' field in {file_path}")
        if not config["systemPrompt"]:
            raise ValueError(f"Missing system prompt content in {file_path}")

        return config

    @staticmethod
    def _parse_simple_frontmatter(frontmatter_yaml: str) -> Dict:
        """Fallback parser for frontmatter that's not valid YAML.

        Handles cases where the description field contains complex multi-line
        strings with special characters that break YAML parsing.
        """
        frontmatter = {}

        # Split into lines and parse key: value pairs
        lines = frontmatter_yaml.split("\n")
        current_key = None
        current_value = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if line starts with a key (has : and doesn't start with space/dash)
            if ":" in line and not line.startswith((" ", "-")):
                # Save previous key-value pair
                if current_key:
                    frontmatter[current_key] = "\n".join(current_value).strip()

                # Start new key-value pair
                key, value = line.split(":", 1)
                current_key = key.strip()
                current_value = [value.strip()] if value.strip() else []
            else:
                # Continuation of current value
                if current_key:
                    current_value.append(line)

        # Save the last key-value pair
        if current_key:
            frontmatter[current_key] = "\n".join(current_value).strip()

        return frontmatter
