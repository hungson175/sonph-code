# Implementation Notes: Customized Agents System

## Overview

The goal is to implement a dynamic agent system where agents are defined in `.md` files under `~/.claude/agents/` and loaded at runtime, similar to how Claude Code's internal agents work.

## Current State Analysis

### Internal Agents Structure (from `/docs/agents/internal_agents.md`)

**Built-in agents are defined with JavaScript-like config objects:**
```javascript
var Hv1={
  agentType:"general-purpose",
  whenToUse:"General-purpose agent for researching complex questions, searching for code, and executing multi-step tasks. When you are searching for a keyword or file and are not confident that you will find the right match in the first few tries use this agent to perform the search for you.",
  tools:["*"],
  systemPrompt:`You are an agent for Claude Code...`,
  source:"built-in",
  baseDir:"built-in", 
  model:"sonnet"
};
```

### Task Tool Dynamic Description Problem

**Current Issue:** The Task tool has a hardcoded docstring:
```python
"""Launch a new agent to handle complex, multi-step tasks autonomously. 

Available agent types and the tools they have access to:
- general-purpose: General-purpose agent for researching complex questions...
- ui-ux-designer: Use this agent when you need expert guidance...  # ← HARDCODED!
"""
```

**Required:** This description must be **generated at runtime** by scanning available agents.

## Implementation Plan

### 1. Agent Configuration Format

**Location:** `~/.claude/agents/ui-ux-designer.md`

**Format:** Markdown with structured sections:
```markdown
# UI-UX Designer Agent

## Agent Type
ui-ux-designer

## When To Use
Use this agent when you need expert guidance on user interface design, user experience optimization, design systems, accessibility, usability testing, or visual design decisions. Examples: <example>Context: User is working on a financial dashboard and needs design guidance. user: 'I'm building a portfolio summary page for our wealth management app. What's the best way to display portfolio performance data?' assistant: 'Let me use the ui-ux-designer agent to provide expert design guidance for your portfolio dashboard.' <commentary>The user needs UI/UX expertise for designing a financial interface, so use the ui-ux-designer agent.</commentary></example>

## Tools
- Task
- Bash  
- Glob
- Grep
- LS
- ExitPlanMode
- Read
- NotebookRead
- WebFetch
- TodoWrite
- WebSearch
- mcp__ide__getDiagnostics
- mcp__ide__executeCode

## Model
sonnet

## System Prompt
You are a UI/UX design expert with deep knowledge of modern design principles, accessibility standards (WCAG), and user experience optimization.

Your specializations:
- Design systems (Material Design, Ant Design, Chakra UI, etc.)
- Accessibility auditing and WCAG compliance
- User flow analysis and optimization
- Visual hierarchy and information architecture
- Component design patterns
- Responsive design principles

Guidelines for analysis:
- Always read existing UI code/markup first to understand current implementation
- Look for design patterns, inconsistencies, and improvement opportunities
- Consider accessibility implications in all recommendations
- Provide specific, actionable advice with code examples when relevant
- Focus on user experience impact of design decisions

When analyzing interfaces:
1. Structure Analysis: Read component files, CSS, and layout code
2. Pattern Recognition: Identify design patterns and anti-patterns
3. Accessibility Review: Check for WCAG violations and improvements
4. UX Evaluation: Assess user flow, information hierarchy, and usability
5. Recommendations: Provide prioritized, actionable improvements

Always provide concrete examples and avoid generic advice.
```
Reviewed notes: The above md is almost correct ( the content of the file is DIFFERRENT in format, read file to understand the format)
For AI: read the file to understand the format and try to write & test the parser for several agent .md files (in that same dir ~/.claude/agents/) . TEST it, if you parse correct ! write it coding_agent/experiments

### 2. Agent Configuration Parser

**New File:** `coding_agent/core/agent_config_parser.py`

```python
import re
from pathlib import Path
from typing import Dict, List, Optional

class AgentConfigParser:
    """Parse agent configuration from .md files."""
    
    @staticmethod
    def parse_agent_md(file_path: Path) -> Dict:
        """Parse agent .md file into config dict."""
        with open(file_path, 'r') as f:
            content = f.read()
        
        config = {}
        
        # Extract sections using regex
        config['agentType'] = AgentConfigParser._extract_section(content, 'Agent Type')
        config['whenToUse'] = AgentConfigParser._extract_section(content, 'When To Use')
        config['tools'] = AgentConfigParser._extract_tools_list(content)
        config['model'] = AgentConfigParser._extract_section(content, 'Model') or 'sonnet'
        config['systemPrompt'] = AgentConfigParser._extract_section(content, 'System Prompt')
        
        # Add metadata
        config['source'] = 'user-defined'
        config['baseDir'] = str(file_path.parent)
        config['configFile'] = str(file_path)
        
        return config
    
    @staticmethod
    def _extract_section(content: str, section_name: str) -> Optional[str]:
        """Extract content under ## Section Name."""
        pattern = rf'^## {re.escape(section_name)}\s*\n(.*?)(?=^## |\Z)'
        match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
        return match.group(1).strip() if match else None
    
    @staticmethod
    def _extract_tools_list(content: str) -> List[str]:
        """Extract tools from ## Tools section as list."""
        tools_section = AgentConfigParser._extract_section(content, 'Tools')
        if not tools_section:
            return ['*']
        
        # Parse bullet points
        tools = []
        for line in tools_section.split('\n'):
            line = line.strip()
            if line.startswith('- '):
                tools.append(line[2:].strip())
        
        return tools or ['*']
```

### 3. Agent Registry System

**New File:** `coding_agent/core/agent_registry.py`

```python
from pathlib import Path
from typing import Dict, List
from .agent_config_parser import AgentConfigParser
from .base_agent import BaseAgent
from .dynamic_agent import DynamicAgent

class AgentRegistry:
    """Registry for discovering and loading agents."""
    
    _instance = None
    _agents_cache = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_available_agents(self) -> Dict[str, Dict]:
        """Get all available agents (built-in + user-defined)."""
        if self._agents_cache is None:
            self._agents_cache = {}
            
            # Add built-in agents
            self._agents_cache['general-purpose'] = {
                'agentType': 'general-purpose',
                'whenToUse': 'General-purpose agent for researching complex questions, searching for code, and executing multi-step tasks. When you are searching for a keyword or file and are not confident that you will find the right match in the first few tries use this agent to perform the search for you.',
                'tools': ['*'],
                'source': 'built-in'
            }
            
            # Scan user-defined agents
            agent_dir = Path.home() / '.claude' / 'agents'
            if agent_dir.exists():
                for md_file in agent_dir.glob('*.md'):
                    try:
                        config = AgentConfigParser.parse_agent_md(md_file)
                        agent_type = config.get('agentType')
                        if agent_type:
                            self._agents_cache[agent_type] = config
                    except Exception as e:
                        print(f"Warning: Failed to load agent {md_file}: {e}")
        
        return self._agents_cache
    
    def load_agent(self, agent_type: str) -> BaseAgent:
        """Load specific agent instance."""
        agents = self.get_available_agents()
        
        if agent_type not in agents:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        config = agents[agent_type]
        
        if config['source'] == 'built-in':
            # Load built-in agent
            if agent_type == 'general-purpose':
                from .general_purpose_agent import GeneralPurposeAgent
                return GeneralPurposeAgent()
            else:
                raise ValueError(f"Unknown built-in agent: {agent_type}")
        else:
            # Load user-defined agent
            return DynamicAgent.from_config(config)
    
    def clear_cache(self):
        """Clear agents cache to reload from disk."""
        self._agents_cache = None
```

### 4. Dynamic Agent Implementation

**New File:** `coding_agent/core/dynamic_agent.py`

```python
from typing import List, Dict
from langchain_core.tools import BaseTool
from .base_agent import BaseAgent
from .config import Config

class DynamicAgent(BaseAgent):
    """Agent created from user configuration."""
    
    @classmethod
    def from_config(cls, config: Dict, model_name: str = None):
        """Create agent from parsed config."""
        tools = cls._resolve_tools(config.get('tools', ['*']))
        
        return cls(
            system_prompt=config.get('systemPrompt', ''),
            tools=tools,
            model_name=model_name or config.get('model', Config.MODEL_NAME)
        )
    
    @staticmethod
    def _resolve_tools(tool_names: List[str]) -> List[BaseTool]:
        """Convert tool name strings to tool instances."""
        if tool_names == ['*']:
            # All tools except Task (prevent recursion)
            from ..tools.file_tools import read_file, write_file, edit_file, list_files
            from ..tools.search_tools import glob_files, grep_files
            from ..tools.execution_tools import run_command, get_bash_output, todo_write
            
            return [
                read_file, write_file, edit_file, list_files,
                glob_files, grep_files, run_command, get_bash_output, todo_write
            ]
        
        # Map tool names to instances
        tool_map = {
            'Read': read_file,
            'Write': write_file, 
            'Edit': edit_file,
            'LS': list_files,
            'Glob': glob_files,
            'Grep': grep_files,
            'Bash': run_command,
            'BashOutput': get_bash_output,
            'TodoWrite': todo_write,
            # Add other tools as needed
        }
        
        tools = []
        for tool_name in tool_names:
            if tool_name in tool_map:
                tools.append(tool_map[tool_name])
            else:
                print(f"Warning: Unknown tool '{tool_name}' - skipping")
        
        return tools
```

### 5. Dynamic Task Tool

**Modified:** `coding_agent/tools/task_tool.py`

```python
from pathlib import Path
from ..core.agent_registry import AgentRegistry

def _generate_task_description() -> str:
    """Generate Task tool description with all available agents."""
    registry = AgentRegistry()
    agents = registry.get_available_agents()
    
    base_description = "Launch a new agent to handle complex, multi-step tasks autonomously.\n\nAvailable agent types and the tools they have access to:"
    
    agent_lines = []
    for agent_type, config in agents.items():
        when_to_use = config.get('whenToUse', '')
        tools = config.get('tools', ['*'])
        tools_str = ', '.join(tools) if tools != ['*'] else '*'
        
        agent_lines.append(f"- {agent_type}: {when_to_use} (Tools: {tools_str})")
    
    usage_notes = """
When using the Task tool, you must specify a subagent_type parameter to select which agent type to use.

When NOT to use the Agent tool:
- If you want to read a specific file path, use the Read or Glob tool instead of the Agent tool, to find the match more quickly
- If you are searching for a specific class definition like "class Foo", use the Glob tool instead, to find the match more quickly
- If you are searching for code within a specific file or set of 2-3 files, use the Read tool instead of the Agent tool, to find the match more quickly
- Other tasks that are not related to the agent descriptions above

Usage notes:
1. Launch multiple agents concurrently whenever possible, to maximize performance; to do that, use a single message with multiple tool uses
2. When the agent is done, it will return a single message back to you. The result returned by the agent is not visible to the user. To show the user the result, you should send a text message back to the user with a concise summary of the result.
3. Each agent invocation is stateless. You will not be able to send additional messages to the agent, nor will the agent be able to communicate with you outside of its final report. Therefore, your prompt should contain a highly detailed task description for the agent to perform autonomously and you should specify exactly what information the agent should return back to you in its final and only message to you.
4. The agent's outputs should generally be trusted
5. Clearly tell the agent whether you expect it to write code or just to do research (search, file reads, web fetches, etc.), since it is not aware of the user's intent
6. If the agent description mentions that it should be used proactively, then you should try your best to use it without the user having to ask for it first. Use your judgement.

Args:
    description: A short (3-5 word) description of the task
    prompt: The task for the agent to perform
    subagent_type: The type of specialized agent to use for this task

Returns:
    str: The agent's complete response after completing the task"""
    
    return base_description + '\n' + '\n'.join(agent_lines) + usage_notes

def create_task_tool():
    """Create Task tool with dynamic agent description."""
    description = _generate_task_description()
    
    @tool("Task")
    def task(
        description: Annotated[str, "A short (3-5 word) description of the task"],
        prompt: Annotated[str, "The task for the agent to perform"], 
        subagent_type: Annotated[str, "The type of specialized agent to use for this task"]
    ) -> str:
        registry = AgentRegistry()
        
        try:
            agent = registry.load_agent(subagent_type)
            result = agent.chat(prompt)
            return f"Task completed: {description}\n\nAgent Response:\n{result}"
        except Exception as e:
            return f"Error executing task '{description}' with {subagent_type} agent: {str(e)}"
    
    # Set the dynamic description
    task.__doc__ = description
    return task
```

### 6. Integration Points

**Modified:** `coding_agent/core/agent.py`
```python
from ..tools.task_tool import create_task_tool  # Import factory

class CodingAgent(BaseAgent):
    def _get_coding_tools(self):
        return [
            read_file, write_file, edit_file, run_command,
            list_files, glob_files, grep_files, get_bash_output,
            todo_write,
            create_task_tool(),  # ← Dynamic Task tool
        ]
```

## Key Benefits

1. **Runtime Discovery**: Agents are discovered by scanning `~/.claude/agents/` on startup
2. **Dynamic Task Tool**: Task tool description updates automatically when agents are added
3. **User Extensible**: Users can add agents without modifying code
4. **Markdown Format**: Human-readable configuration format
5. **Flexible Tools**: Each agent can specify which tools it needs
6. **Caching**: Agent registry caches configurations for performance

## Usage Flow

1. **User creates** `~/.claude/agents/ui-ux-designer.md`
2. **System startup** → AgentRegistry scans directory → finds new agent
3. **Task tool creation** → Generates description including new agent
4. **LLM sees** updated Task tool with ui-ux-designer option
5. **Task delegation** → `task(..., subagent_type="ui-ux-designer")` works automatically

## File Structure

```
~/.claude/
  agents/
    ui-ux-designer.md
    code-reviewer.md
    security-auditor.md

coding_agent/
  core/
    agent_registry.py
    agent_config_parser.py
    dynamic_agent.py
  tools/
    task_tool.py  # Modified to use create_task_tool()
```

This approach maintains the same extensibility as Claude Code's internal agent system while using a user-friendly markdown configuration format.