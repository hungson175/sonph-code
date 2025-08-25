# Notes: Experience Updating Prompts from JSON API Requests

## Context

The user emphasized that the original Claude Code API request data contains "master piece" prompt engineering that should be preserved **exactly** - not even one character should be changed. This led to a systematic process of extracting original descriptions from JSON files and updating both documentation and implementation code.

## Process Overview

### 1. JSON File Analysis → Documentation Update → Code Update

**Workflow:**
```
JSON API Request Data → Extract Tool Description → Update .md Docs → Update Code Implementation
```

**Files Involved:**
- **Source**: `/Users/sonph36/dev/demo/sonph-code/data/[X] Request - api.anthropic.com_v1_messages.json`
- **Documentation**: `/Users/sonph36/dev/demo/sonph-code/docs/claude-code/*.md`
- **Implementation**: `/Users/sonph36/dev/demo/sonph-code/coding_agent/tools/*.py`

## Key Lessons Learned

### 1. **JSON String Escaping is Critical**

**Problem**: Direct copying from JSON loses proper newlines and escaping.

**Solution**: Use Python to properly handle JSON string conversion:
```python
import json
with open('data/request.json', 'r') as f:
    data = json.load(f)
    tool = next(tool for tool in data['tools'] if tool['name'] == 'ToolName')
    description = tool['description']  # Automatically handles \n and \'
```

**Key Insight**: The `repr()` output shows escaped sequences, but `json.load()` automatically converts them to proper strings.

### 2. **Newline Characters Matter**

**Original JSON**: Contains `\n` sequences that must become actual newlines
**Escaped Quotes**: Contains `\'` that must become proper single quotes

**Example**:
```
JSON: "Usage notes:\n  - The command argument is required.\n  - You can specify..."
Should become:
Usage notes:
  - The command argument is required.
  - You can specify...
```

### 3. **Tool Description vs Function Implementation**

**Two Different Updates Needed:**

1. **Documentation Update** (`docs/claude-code/*.md`):
   - Pure documentation for reference
   - Complete original description with schema
   
2. **Code Implementation Update** (`coding_agent/tools/*.py`):
   - Docstring in `@tool` decorator function
   - Must match original exactly for LLM prompt engineering
   - Parameters must align with original schema

### 4. **Parameter Alignment is Critical**

**Original Schema**:
```json
{
  "properties": {
    "command": {"type": "string"},
    "description": {"type": "string"},
    "timeout": {"type": "number"},
    "run_in_background": {"type": "boolean"}
  }
}
```

**Function Must Match**:
```python
@tool("Bash")
def run_command(
    command: str,
    description: str = "",  # ← Must include even if not used in implementation
    timeout: int = 120,
    run_in_background: bool = False,
) -> str:
```

## Specific Examples

### Task Tool Update

**Source**: `data/[515] Request - api.anthropic.com_v1_messages.json`

**Challenge**: Massive description with multiple agent types, examples, and usage notes

**Key Learning**: The `whenToUse` descriptions from internal agents are directly integrated into the Task tool description. This creates the dynamic agent selection capability.

### Bash Tool Update

**Source**: `data/[16] Request - api.anthropic.com_v1_messages.json`

**Challenge**: Complex description with git workflows, PR creation, and extensive usage guidelines

**Key Learning**: The comprehensive workflows (commit process, PR creation) are part of the tool prompt engineering - not separate documentation.

## Technical Implementation Notes

### Python Script Pattern for Updates

```python
import json

# 1. Extract original description
with open('data/request.json', 'r') as f:
    data = json.load(f)
    tool_desc = next(tool for tool in data['tools'] if tool['name'] == 'ToolName')['description']

# 2. Update documentation
doc_content = f"""# Tool Name

## Description

{tool_desc}

## Schema
[... schema content ...]
"""

with open('docs/claude-code/ToolName.md', 'w') as f:
    f.write(doc_content)

# 3. Update code docstring (requires careful string replacement)
```

### String Replacement Challenges

**Problem**: Docstrings in Python files need precise replacement without breaking code structure.

**Solution**: Find docstring boundaries carefully:
```python
# Find function decorator
start = content.find('@tool("ToolName")')
# Find docstring start/end
docstring_start = content.find('"""', start)
docstring_end = content.find('"""', docstring_start + 3)
# Replace content between docstring markers
new_content = content[:docstring_start + 3] + original_desc + content[docstring_end:]
```

## Why This Matters

### 1. **LLM Prompt Engineering**
The original descriptions are carefully crafted to guide LLM behavior. Any changes can affect:
- When tools are used
- How parameters are chosen  
- What workflows are followed

### 2. **Multi-Agent Coordination**
The Task tool description includes agent `whenToUse` patterns that enable:
- Automatic agent selection
- Proactive tool usage
- Context-aware delegation

### 3. **Behavioral Consistency**
Original prompts ensure the reimplemented tools behave exactly like Claude Code:
- Same usage patterns
- Same restrictions and guidelines
- Same error handling approaches

## Process Validation

### After Each Update:

1. **Test Tool Import**: `python -c "from coding_agent.tools.tool_name import tool_function"`
2. **Check Docstring**: Verify LangChain can read the tool description
3. **Parameter Alignment**: Ensure function signature matches JSON schema
4. **Behavioral Testing**: Test that tool behaves as expected

## Future Improvements

### 1. **Automated Validation**
Create script to validate that tool implementations match original JSON schemas.

### 2. **Dynamic Tool Registry**
Implement system where tools are loaded from configuration, making updates easier.

### 3. **Prompt Engineering Documentation**
Document the specific prompt engineering patterns found in original tools.

## Universal Lessons for Future Updates

### 1. **Apply to System Prompts**
The same precision required for tool descriptions applies to system prompts:
- Extract original system prompt from JSON API request data
- Preserve exact wording, formatting, and structure
- System prompts are equally critical for LLM behavior as tool descriptions

### 2. **Apply to All Code Components**
This methodology extends beyond tools to:
- **Agent implementations**: Match original behavior patterns exactly
- **Message handling**: Preserve original conversation flow structures
- **Error handling**: Maintain original error message formats
- **Configuration**: Keep original parameter names and types

### 3. **Documentation as Source of Truth**
The original JSON API data serves as the definitive reference for:
- System behavior specifications
- Tool interaction patterns
- Agent delegation logic
- User experience consistency

### 4. **Validation Process for Any Component**
Before updating any component:
1. **Find Source**: Locate original specification in JSON data
2. **Extract Precisely**: Use Python JSON parsing, never manual copying
3. **Update Systematically**: Documentation first, then implementation
4. **Validate Behavior**: Test that changes maintain original functionality
5. **Preserve Engineering**: Never "improve" original prompt engineering

## Conclusion

The process of updating from JSON → Docs → Code requires extreme precision to preserve the "master piece" prompt engineering. The key is understanding that these descriptions are not just documentation - they are behavioral programming for the LLM system.

**Most Important Insight**: Never modify original prompt engineering, even for "improvements" - the original authors spent significant effort crafting these prompts for optimal LLM behavior.

**Universal Application**: This methodology applies to ALL components of the system - tools, system prompts, agents, and any other behavioral specifications found in the original API data.