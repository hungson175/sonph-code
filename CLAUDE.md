# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based coding agent implementation that mimics Claude Code functionality. The project implements a command-line tool with essential coding capabilities using LangChain and Anthropic's API.

## Architecture

The codebase is structured as a single-file Python application (`coding_agent.py`) with the following key components:

### Core Components

- **CodingAgent Class**: Main orchestrator that manages LLM interactions, tool execution, and conversation state
- **Tool System**: Collection of essential coding tools implemented as LangChain tools:
  - File operations: Read, Write, Edit, MultiEdit
  - Directory operations: LS, Glob, Grep  
  - Command execution: Bash, BashOutput
  - Task management: TodoWrite
- **Message Management**: Handles conversation history with caching optimization using Anthropic's cache control
- **Background Shell Support**: Allows long-running commands via background bash processes

### Key Files

- `coding_agent.py` - Main implementation with all tools and agent logic
- `data/` - Contains sample API requests and outputs for testing/reference
- `docs/claude-code/` - Documentation for individual tools (reference only)

## Development Commands

### Project Setup

```bash
# Install dependencies using uv (recommended)
uv sync

# Activate virtual environment
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate     # On Windows
```

### Running the Agent

```bash
# Using uv (recommended)
uv run python coding_agent.py

# Or with activated venv
python coding_agent.py

# When prompted, choose:
# 1 - Run demo
# 2 - Interactive mode
```

### Development Tools

```bash
# Format code
uv run black coding_agent.py

# Lint code
uv run ruff check coding_agent.py

# Run tests
uv run pytest
```

### Dependencies

The project uses:
- `langchain-anthropic>=0.1.0` - For LLM integration
- `langchain-core>=0.1.0` - Core LangChain functionality  
- `python-dotenv>=1.0.0` - Environment variable management
- `colorama>=0.4.0` - Terminal color output

Development dependencies:
- `pytest>=7.0.0` - Testing framework
- `black>=23.0.0` - Code formatter
- `ruff>=0.1.0` - Fast Python linter

### Environment Setup

Environment configuration is required for the agent to work:

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Configure required variables in `.env`:**
   - `ANTHROPIC_API_KEY` - Required for LLM API access (get from https://console.anthropic.com/)
   - `LANGSMITH_*` variables - Optional LangSmith tracing configuration (get from https://smith.langchain.com/)

## Code Conventions

- **Model**: Uses `claude-sonnet-4-20250514` by default (configurable via `MODEL_NAME` constant)
- **Error Handling**: Tools return descriptive error messages rather than raising exceptions
- **File Paths**: All file operations require absolute paths
- **Caching**: Uses Anthropic's ephemeral cache control for system prompts and recent messages to optimize token usage
- **Tool Organization**: Each tool is implemented as a `@tool` decorated function with comprehensive docstrings

## Tool Implementation Patterns

- **File Operations**: Always validate paths and provide clear error messages
- **Command Execution**: Support both synchronous and background execution modes
- **Search Operations**: Implement both file-based (Glob) and content-based (Grep) searching
- **State Management**: Maintain conversation history and background process tracking
- **TodoWrite**: NEVER, EVER modify this tool - it's a master piece of engineering with intentionally minimalist implementation

## CRITICAL: Tool Description Preservation

⚠️ **NEVER modify tool descriptions in `docs/claude-code/*.md`** - they are MASTER PIECES of prompt engineering from Claude Code reverse engineering. Only change if there's a specific bug or non-existent tool/code referenced.

## Testing

No automated test framework is currently configured. The project includes a demo mode that exercises core functionality.

## Development Workflow

When modifying this codebase:
1. Test changes using the interactive mode
2. Verify all tools work correctly with the demo scenarios
3. Ensure error handling is robust for edge cases
4. Maintain the single-file architecture unless refactoring is necessary

## Key Implementation Details

- Background shell processes are tracked in `_background_shells` global dictionary
- Message caching optimizes token usage by marking system prompts and recent messages with cache control
- Tools are converted to Anthropic format with the last tool receiving cache control for optimization
- Working directory is maintained as instance state to support `cd` operations