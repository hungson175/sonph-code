# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based coding agent that replicates Claude Code functionality using LangChain and Anthropic's API. The project demonstrates reverse engineering of Claude Code through API interception and reimplementation of essential coding tools.

## Development Commands

### Environment Setup
```bash
# Install dependencies
uv sync

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys:
# - ANTHROPIC_API_KEY for Claude/Anthropic (required for Claude provider)
# - DEEPSEEK_API_KEY for DeepSeek (required for DeepSeek provider)
# - Optional LANGSMITH_* keys for tracing
```

### Running the Agent

#### Using the Global Launcher (Recommended)
```bash
# Run in current directory with default provider (DeepSeek)
sonph-code

# Specify LLM provider
sonph-code --llm claude     # Use Claude/Anthropic
sonph-code --llm deepseek   # Use DeepSeek (default)

# Run in specific directory with provider
sonph-code /path/to/project --llm claude

# Show help
sonph-code --help
```

#### Direct Python Execution
```bash
# Primary way to run
uv run python main.py

# Alternative with activated venv
source .venv/bin/activate
python main.py
```

### Code Quality
```bash
# Format code
uv run black .

# Lint code
uv run ruff check .
uv run ruff check . --fix  # Auto-fix issues

# Run tests (if any exist)
uv run pytest
```

## Architecture

### Core Components

The project now uses a modular architecture:

**main.py** - Main entry point containing interactive CLI interface

**coding_agent/** - Modular package structure:
- `core/` - Core components (CodingAgent class, configuration, shell management)
- `tools/` - Tool implementations (Read, Write, LS, Glob, Bash, BashOutput, TodoWrite)
- `commands/` - Command management (native and custom commands)
- `utils/` - Utility functions (context loading, keyboard handling)

**coding_agent.py** - Original single-file implementation (preserved for safety/reference)

### Key Design Patterns

**Tool Architecture**: Each tool is implemented as a `@tool` decorated function with comprehensive docstrings that serve as both documentation and prompt engineering. The tool descriptions are critical - they are described as "MASTER PIECES of prompt engineering" and should not be modified unless there's a specific bug.

**Background Process Management**: `BackgroundShellManager` class for managing long-running bash processes with cancellation support via Esc key or Ctrl+C.

**Caching Strategy**: Uses Anthropic's ephemeral caching on the last tool and system/user messages to optimize API calls.

**Message Flow**: Maintains conversation history with SystemMessage + HumanMessage + ToolMessage pattern, following LangChain conventions.

## Dependencies

### Required External Tools
- **ripgrep (rg)**: Essential for Grep tool functionality. Install via:
  - macOS: `brew install ripgrep`
  - Ubuntu/Debian: `sudo apt install ripgrep`
  - Windows: `winget install BurntSushi.ripgrep.MSVC`

### Python Dependencies
- `langchain-anthropic`: Core LLM integration
- `langchain-core`: Tool and message abstractions
- `python-dotenv`: Environment variable management
- `colorama`: Terminal color output

## Environment Variables

Required (choose based on LLM provider):
- `ANTHROPIC_API_KEY`: Get from https://console.anthropic.com/ (for Claude provider)
- `DEEPSEEK_API_KEY`: Get from https://platform.deepseek.com/ (for DeepSeek provider)

Optional (for tracing):
- `LANGSMITH_TRACING=true`
- `LANGSMITH_API_KEY`: Get from https://smith.langchain.com/
- `LANGSMITH_PROJECT`: Your project name

## Interactive Commands

Within the agent CLI:
- `quit`/`exit`: Exit the agent
- `reset`: Reset conversation history
- `pwd`: Show current working directory
- `cd <path>`: Change working directory
- `/init`: Analyze codebase and create/update CLAUDE.md (native command)
- `/commands`: List all available native and custom commands
- `/memory`: View current memory context
- `/model`: Switch LLM provider or show current model info
- `Ctrl+C` or `Esc`: Cancel long-running tool execution

### LLM Provider Management

The agent supports multiple LLM providers that can be switched dynamically:

#### Available Providers
- **Claude/Anthropic** (aliases: `claude`, `sonnet`)
  - Requires `ANTHROPIC_API_KEY`
  - Default model: `claude-sonnet-4-20250514`
  - Features: Manual cache control, optimized token usage reporting
- **DeepSeek** (aliases: `deepseek`, `ds`)
  - Requires `DEEPSEEK_API_KEY`
  - Default model: `deepseek-chat`
  - Features: Auto-cache management, cost-effective inference

#### Using the `/model` Command
```bash
# Show current model and available providers
/model

# Switch to Claude
/model claude

# Switch to DeepSeek
/model deepseek

# Switch with specific model name
/model sonnet claude-sonnet-4-20250514
```

#### Command-line Provider Selection
```bash
# Start with specific provider
sonph-code --llm claude
sonph-code --llm deepseek
```

## Reverse Engineering Documentation

The `docs/` directory contains extracted Claude Code system prompts and tool descriptions from API interception using Proxyman. The `data/` directory contains sample API requests/responses. These serve as reference for maintaining fidelity to original Claude Code behavior.

## Example Projects

The `example_projects/` directory contains generated projects (caro game, expense trackers) that demonstrate the agent's capabilities. These are excluded from git via `.gitignore`.

# HUMAN NOTES - note for human - AI don't read this
- WOW , review all tools desc, it may be wrong (like Task tool !)