"""Agent registry for discovering and loading dynamic agents."""

from pathlib import Path
from typing import Dict, List
from .agent_config_parser import AgentConfigParser


class AgentRegistry:
    """Registry for discovering and loading agents from ~/.claude/agents/."""

    _instance = None
    _agents_cache = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_available_agents(self) -> Dict[str, Dict]:
        """Get all available agents (built-in + user-defined).

        Returns:
            Dict mapping agent_type -> agent_config
        """
        if self._agents_cache is None:
            self._agents_cache = {}

            # Add built-in agents
            self._agents_cache["general-purpose"] = {
                "agentType": "general-purpose",
                "whenToUse": "General-purpose agent for researching complex questions, searching for code, and executing multi-step tasks. When you are searching for a keyword or file and are not confident that you will find the right match in the first few tries use this agent to perform the search for you.",
                "tools": ["*"],
                "model": "sonnet",
                "source": "built-in",
            }

            # Scan user-defined agents
            agent_dir = Path.home() / ".claude" / "agents"
            if agent_dir.exists():
                for md_file in agent_dir.glob("*.md"):
                    try:
                        config = AgentConfigParser.parse_agent_md(md_file)
                        agent_type = config.get("agentType")
                        if agent_type:
                            self._agents_cache[agent_type] = config
                    except Exception as e:
                        print(f"Warning: Failed to load agent {md_file}: {e}")

        return self._agents_cache

    def get_agent_list_for_task_tool(self) -> List[str]:
        """Get formatted list of agents for Task tool description.

        Returns:
            List of strings formatted as: "- agent-name: description (Tools: tools)"
        """
        agents = self.get_available_agents()
        agent_lines = []

        for agent_type, config in agents.items():
            when_to_use = config.get("whenToUse", "")
            tools = config.get("tools", ["*"])
            tools_str = ", ".join(tools) if tools != ["*"] else "*"

            agent_lines.append(f"- {agent_type}: {when_to_use} (Tools: {tools_str})")

        return agent_lines

    def load_agent(self, agent_type: str):
        """Load specific agent instance.

        Args:
            agent_type: The type of agent to load

        Returns:
            BaseAgent instance

        Raises:
            ValueError: If agent type is unknown
        """
        agents = self.get_available_agents()

        if agent_type not in agents:
            available = list(agents.keys())
            raise ValueError(
                f"Unknown agent type: {agent_type}. Available: {available}"
            )

        config = agents[agent_type]

        if config["source"] == "built-in":
            # Load built-in agent
            if agent_type == "general-purpose":
                from .general_purpose_agent import GeneralPurposeAgent

                return GeneralPurposeAgent()
            else:
                raise ValueError(f"Unknown built-in agent: {agent_type}")
        else:
            # Load user-defined agent
            from .dynamic_agent import DynamicAgent

            return DynamicAgent.from_config(config)

    def clear_cache(self):
        """Clear agents cache to reload from disk."""
        self._agents_cache = None

    def get_agent_count(self) -> Dict[str, int]:
        """Get count of different agent types."""
        agents = self.get_available_agents()
        built_in = sum(
            1 for config in agents.values() if config["source"] == "built-in"
        )
        user_defined = sum(
            1 for config in agents.values() if config["source"] == "user-defined"
        )

        return {
            "built_in": built_in,
            "user_defined": user_defined,
            "total": built_in + user_defined,
        }
