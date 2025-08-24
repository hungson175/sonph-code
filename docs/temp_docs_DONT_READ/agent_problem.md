# Agent Architecture Problem & Solution

## Current Problem

The `create_general_purpose_agent()` function has a fundamental architectural flaw:

```python
def create_general_purpose_agent():
    agent = CodingAgent()  # ❌ Fully initialized with default prompt
    
    # ❌ Trying to override AFTER initialization
    agent.system_prompt_str = general_purpose_prompt
    agent.messages[0].content = agent._create_cached_message(general_purpose_prompt)
    
    return agent  # ❌ LLM is still bound with original prompt!
```

### Why This Fails

1. **`CodingAgent()` constructor flow**:
   - `self.llm = ChatAnthropic(...)` - Creates LLM
   - `self.tools, self.tools_map, self.llm_with_tools = self._setup_tools()` - **Binds tools with DEFAULT system prompt**
   - `self.system_prompt_str = coding_agent_prompt()` - Sets default prompt
   - `self.messages = [SystemMessage(...)]` - Creates message history

2. **Problem**: By the time we try to "override" the prompt, the `llm_with_tools` is already created and bound with the **default** system prompt.

3. **Result**: The sub-agent actually uses the same system prompt as the main agent, defeating the purpose of specialization.

## Root Cause

**`CodingAgent` is a concrete class**, not a configurable base class. It hard-codes:
- Specific system prompt (`coding_agent_prompt()`)
- Specific tool set (all tools)
- Specific behavior patterns

The Task tool needs **different agent types** with different:
- System prompts (coding vs research vs design)
- Tool sets (some agents shouldn't have Task tool to avoid recursion)
- Behavioral patterns

## Solution: Refactor to Base Agent Architecture

### 1. Create `BaseAgent` Class

```python
class BaseAgent:
    def __init__(self, 
                 system_prompt: str,
                 tools: List[BaseTool] = None,
                 model_name: str = Config.MODEL_NAME):
        """Configurable agent base class."""
        self.system_prompt_str = system_prompt
        self.tools = tools or self._get_default_tools()
        
        # Setup LLM and bind tools AFTER prompt is set
        self.llm = ChatAnthropic(model=model_name, temperature=0.0, max_tokens=16384)
        self.tools_map, self.llm_with_tools = self._setup_tools()
        
        # Initialize with correct prompt
        self.messages = [SystemMessage(content=self._create_cached_message(system_prompt))]
```

### 2. Refactor `CodingAgent` to Extend `BaseAgent`

```python
class CodingAgent(BaseAgent):
    def __init__(self, model_name: str = Config.MODEL_NAME):
        # Initialize command managers
        self.command_manager = CustomCommandManager()
        self.native_command_manager = NativeCommandManager()
        
        # Load memory context
        self.memory_context = load_memory_context()
        
        # Call parent with coding-specific configuration
        super().__init__(
            system_prompt=coding_agent_prompt(),
            tools=self._get_coding_tools(),
            model_name=model_name
        )
        
        # Add memory context if exists
        if self.memory_context and len(self.memory_context.strip()) > 100:
            self.messages.append(
                HumanMessage(content=self._create_cached_message(self.memory_context))
            )
```

### 3. Create Specialized Agent Classes

```python
class GeneralPurposeAgent(BaseAgent):
    def __init__(self, model_name: str = Config.MODEL_NAME):
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
        return """You are an agent for Claude Code, specialized in research and analysis..."""
    
    def _get_research_tools(self) -> List[BaseTool]:
        # All tools EXCEPT Task tool to prevent infinite recursion
        return [read_file, write_file, edit_file, run_command, 
                list_files, glob_files, grep_files, get_bash_output, todo_write]
```

### 4. Update Task Tool

```python
def create_general_purpose_agent():
    """Create a specialized research agent."""
    return GeneralPurposeAgent()

@tool("Task")
def task(description: str, prompt: str, subagent_type: str) -> str:
    # Create appropriate specialized agent
    if subagent_type == "general-purpose":
        agent = GeneralPurposeAgent()
    # elif subagent_type == "faang-engineer-architect":
    #     agent = FaangEngineerAgent()
    # etc...
    
    result = agent.chat(prompt)
    return f"Task completed: {description}\n\nAgent Response:\n{result}"
```

## Benefits of This Architecture

1. **Proper Initialization**: Each agent type initialized with correct prompt from the start
2. **Tool Isolation**: Different agents can have different tool sets (prevents recursion)
3. **Extensible**: Easy to add new agent types (FaangEngineerAgent, UiUxAgent, etc.)
4. **Clean Separation**: Base class handles common logic, subclasses define specialization
5. **Type Safety**: Each agent type is a distinct class with specific behavior

## Migration Path

1. Create `BaseAgent` class
2. Refactor `CodingAgent` to extend `BaseAgent`  
3. Create `GeneralPurposeAgent` class
4. Update `task_tool.py` to use `GeneralPurposeAgent()`
5. Test to ensure main agent still works
6. Add more specialized agents as needed

This solves the fundamental issue: **agents are properly configured from initialization**, not hacked after creation.