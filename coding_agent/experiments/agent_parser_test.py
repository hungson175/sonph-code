#!/usr/bin/env python3
"""Test parser for agent .md files with YAML frontmatter."""

import yaml
from pathlib import Path
from typing import Dict


class AgentConfigParser:
    """Parse agent configuration from .md files with YAML frontmatter."""

    @staticmethod
    def parse_agent_md(file_path: Path) -> Dict:
        """Parse agent .md file into config dict."""
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
                # Split comma-separated tools
                config["tools"] = [tool.strip() for tool in tools_str.split(",")]
        else:
            config["tools"] = tools_str or ["*"]

        config["model"] = frontmatter.get("model", "sonnet")
        config["color"] = frontmatter.get("color", None)

        # Add metadata
        config["source"] = "user-defined"
        config["baseDir"] = str(file_path.parent)
        config["configFile"] = str(file_path)

        return config

    @staticmethod
    def _parse_simple_frontmatter(frontmatter_yaml: str) -> Dict:
        """Fallback parser for frontmatter that's not valid YAML."""
        frontmatter = {}

        # Split into lines and parse key: value pairs
        lines = frontmatter_yaml.split("\n")
        current_key = None
        current_value = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if line starts with a key
            if ":" in line and not line.startswith(" "):
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


def test_parser():
    """Test the parser with actual agent files."""
    agent_dir = Path.home() / ".claude" / "agents"

    if not agent_dir.exists():
        print(f"❌ Agent directory does not exist: {agent_dir}")
        return

    print(f"🔍 Testing parser with files in: {agent_dir}")
    print()

    agent_files = list(agent_dir.glob("*.md"))
    if not agent_files:
        print(f"❌ No .md files found in {agent_dir}")
        return

    parser = AgentConfigParser()

    for md_file in agent_files:
        print(f"📄 Parsing: {md_file.name}")
        try:
            config = parser.parse_agent_md(md_file)

            # Display parsed config
            print(f"  ✅ Agent Type: {config['agentType']}")
            print(f"  📝 Description: {config['whenToUse'][:100]}...")
            print(f"  🛠️  Tools: {config['tools']}")
            print(f"  🤖 Model: {config['model']}")
            print(f"  🎨 Color: {config['color']}")
            print(f"  📄 System Prompt: {len(config['systemPrompt'])} chars")
            print()

        except Exception as e:
            print(f"  ❌ Error: {e}")
            print()


def generate_task_description_test():
    """Test generating Task tool description from parsed agents."""
    agent_dir = Path.home() / ".claude" / "agents"
    parser = AgentConfigParser()

    print("🔧 Generating Task tool description...")
    print()

    base_description = "Launch a new agent to handle complex, multi-step tasks autonomously.\n\nAvailable agent types and the tools they have access to:"

    agent_lines = []

    # Add built-in general-purpose
    agent_lines.append(
        "- general-purpose: General-purpose agent for researching complex questions, searching for code, and executing multi-step tasks. When you are searching for a keyword or file and are not confident that you will find the right match in the first few tries use this agent to perform the search for you. (Tools: *)"
    )

    # Add user-defined agents
    for md_file in agent_dir.glob("*.md"):
        try:
            config = parser.parse_agent_md(md_file)
            agent_type = config["agentType"]
            when_to_use = config["whenToUse"]
            tools = config["tools"]
            tools_str = ", ".join(tools) if tools != ["*"] else "*"

            agent_lines.append(f"- {agent_type}: {when_to_use} (Tools: {tools_str})")
        except Exception as e:
            print(f"⚠️  Skipping {md_file.name}: {e}")

    full_description = base_description + "\n" + "\n".join(agent_lines)

    print("📋 Generated Task tool description:")
    print("=" * 80)
    print(full_description[:1000])  # First 1000 chars
    print("...")
    print("=" * 80)
    print(f"📏 Total length: {len(full_description)} characters")


if __name__ == "__main__":
    print("🧪 Agent Parser Test")
    print("=" * 50)

    test_parser()

    print("\n" + "=" * 50)
    generate_task_description_test()
