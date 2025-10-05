# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based coding agent that replicates Claude Code functionality using LangChain with support for multiple LLM providers (Grok, Claude/Anthropic, DeepSeek). The project demonstrates reverse engineering of Claude Code through API interception and reimplementation of essential coding tools.

## Development Commands

### Environment Setup
```bash
# Install dependencies
uv sync

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys:
# - XAI_API_KEY for Grok/xAI (REQUIRED - default provider)
# - ANTHROPIC_API_KEY for Claude/Anthropic (optional)
# - DEEPSEEK_API_KEY for DeepSeek (optional)
# - LANGSMITH_* keys for tracing (optional)
```

### Running the Agent

#### Using the Global Launcher (Recommended)
```bash
# Run in current directory (uses Grok by default)
sonph-code

# Run in specific directory
sonph-code /path/to/project

# Show help
sonph-code --help

# To switch LLM providers, use the /model command inside the tool
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

The project uses a modular architecture:

**main.py** - Main entry point with rich CLI interface using prompt_toolkit for autocomplete

**coding_agent/** - Modular package structure:
- `core/` - Core components including CodingAgent class, LLM provider abstraction, and configuration
- `tools/` - Tool implementations (Read, Write, Edit, LS, Glob, Bash, BashOutput, TodoWrite)
- `commands/` - Native and custom command management
- `utils/` - Utility functions for context loading, keyboard handling
- `ui/` - Rich CLI interface with autocomplete functionality

**coding_agent.py** - Original single-file implementation (preserved for reference)

### Key Design Patterns

**Tool Architecture**: Each tool is implemented as a `@tool` decorated function with comprehensive docstrings that serve as both documentation and prompt engineering. The tool descriptions are critical - they are described as "MASTER PIECES of prompt engineering" and should not be modified unless there's a specific bug.

**LLM Provider System**: Abstraction layer supporting multiple LLM providers (Claude, DeepSeek, Grok) with provider-specific cache management and token usage reporting. Default provider is Grok.

**Background Process Management**: `BackgroundShellManager` class for managing long-running bash processes with cancellation support via Esc key or Ctrl+C.

**Caching Strategy**: Uses provider-specific caching - Anthropic's ephemeral caching for Claude, auto-cache management for DeepSeek and Grok.

**Rich CLI with Autocomplete**: Uses prompt_toolkit to provide command autocomplete when typing `/` at the beginning of input. Autocomplete shows inline suggestions automatically.

## Dependencies

### Required External Tools
- **ripgrep (rg)**: Essential for Grep tool functionality. Install via:
  - macOS: `brew install ripgrep`
  - Ubuntu/Debian: `sudo apt install ripgrep`
  - Windows: `winget install BurntSushi.ripgrep.MSVC`

### Python Dependencies
- `langchain-anthropic`: Core LLM integration for Claude
- `langchain-openai`: DeepSeek provider support
- `langchain-xai`: Grok provider support
- `langchain-core`: Tool and message abstractions
- `prompt_toolkit`: Rich CLI with autocomplete
- `rich`: Terminal UI components
- `python-dotenv`: Environment variable management
- `colorama`: Terminal color output

## Environment Variables

Required:
- `XAI_API_KEY`: Get from https://console.x.ai/ (for Grok provider - **REQUIRED**, default)

Optional (for alternative providers):
- `ANTHROPIC_API_KEY`: Get from https://console.anthropic.com/ (for Claude provider)
- `DEEPSEEK_API_KEY`: Get from https://platform.deepseek.com/ (for DeepSeek provider)

Optional:
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
- `/context`: Show context usage visualization
- `Ctrl+C` or `Esc`: Cancel long-running tool execution

### Autocomplete Feature
- Type `/` at the beginning to see command suggestions
- Suggestions appear automatically as gray inline text
- Press TAB to show popup menu with all completions

### LLM Provider Management

The agent supports multiple LLM providers that can be switched dynamically:

#### Available Providers
- **Claude/Anthropic** (aliases: `claude`, `sonnet`)
  - Requires `ANTHROPIC_API_KEY`
  - Model: `claude-sonnet-4-20250514`
  - Features: Manual cache control, optimized token usage
- **DeepSeek** (aliases: `deepseek`, `ds`)
  - Requires `DEEPSEEK_API_KEY`
  - Model: `deepseek-chat`
  - Features: Auto-cache management, cost-effective
- **Grok/xAI** (aliases: `grok`, `xai`) **[DEFAULT]**
  - Requires `XAI_API_KEY`
  - Model: `grok-code-fast-1`
  - Features: Auto-cache management, fast inference

#### Using the `/model` Command
```bash
# Show current model and available providers
/model

# Switch providers
/model claude
/model deepseek
/model grok
```

## Reverse Engineering Documentation

The `docs/` directory contains extracted Claude Code system prompts and tool descriptions from API interception using Proxyman. The `data/` directory contains sample API requests/responses. These serve as reference for maintaining fidelity to original Claude Code behavior.

## Example Projects

The `example_projects/` directory contains generated projects (caro game, expense trackers) that demonstrate the agent's capabilities. These are excluded from git via `.gitignore`.