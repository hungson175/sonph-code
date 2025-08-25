#!/usr/bin/env python3
"""Convert agent .md files to JSON format."""

import json
import sys
from pathlib import Path
from agent_config_parser import AgentConfigParser


def convert_agent_to_json(md_file_path: Path, output_dir: Path):
    """Convert single agent .md file to JSON."""
    print(f"📄 Processing {md_file_path.name}...")

    try:
        # Parse the .md file
        config = AgentConfigParser.parse_agent_md(md_file_path)

        # Create output filename
        agent_type = config["agentType"]
        json_filename = f"{agent_type}.json"
        json_file_path = output_dir / json_filename

        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        # Write JSON file
        with open(json_file_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        print(f"✅ Converted to {json_file_path}")
        return True

    except Exception as e:
        print(f"❌ Error converting {md_file_path.name}: {e}")
        return False


def main():
    """Convert specified agent files to JSON."""
    # Input files
    agents_dir = Path.home() / ".claude" / "agents"
    target_files = ["octalysis-gamification-expert.md", "ui-ux-designer.md"]

    # Output directory
    output_dir = Path("/Users/sonph36/dev/demo/sonph-code/docs/agents")

    print("🔄 Converting Agent .md Files to JSON")
    print("=" * 50)

    success_count = 0

    for filename in target_files:
        md_file = agents_dir / filename

        if not md_file.exists():
            print(f"❌ File not found: {md_file}")
            continue

        if convert_agent_to_json(md_file, output_dir):
            success_count += 1

    print(
        f"\n📊 Results: {success_count}/{len(target_files)} files converted successfully"
    )

    if success_count == len(target_files):
        print("🎉 All agent files converted to JSON!")
        return 0
    else:
        print("💥 Some conversions failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
