<system-reminder>
As you answer the user's questions, you can use the following context:

# claudeMd

Codebase and user instructions are shown below. Be sure to adhere to these instructions. IMPORTANT: These instructions OVERRIDE any default behavior and you MUST follow them exactly as written.

Contents of /Users/sonph36/.claude/CLAUDE.md (user's private global instructions for all projects):

## Development Workflow
IMPORTANT: 
- ./sample_codes dir is reference code, only read when explicitly mentioned - not related to codebase
- Before you make any change, create and checkout a feature branch named "feature_some_short_name". Make and then commit your changes in this branch.
- Before committing, you must: write automated tests for all code, run linting, compile successfully, and ensure ALL tests pass - no basic errors allowed.
- Use standard naming conventions and maintain organized structure - place new files in appropriate directories (docs in `docs/`, tests in `tests/`, etc.), creating folders as needed.

## Python Workflow
- prefer uv over pip if possible
- don't test LLM related codes automatically, it's very costly

Contents of /Users/sonph36/dev/demo/sonph-code/CLAUDE.md (project instructions, checked into the codebase):

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
# Edit .env with your ANTHROPIC_API_KEY and optional LANGSMITH_* keys
```

### Running the Agent
```bash
# Primary way to run (recommended)
uv run python coding_agent.py

# Alternative with activated venv
source .venv/bin/activate
python coding_agent.py
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

**coding_agent.py** - Single-file implementation containing:
- `CodingAgent` class: Main agent orchestrator with LangChain integration
- Tool implementations: Read, Write, LS, Glob, Bash, BashOutput, TodoWrite
- Interactive CLI with keyboard interrupt handling and background process management
- System prompt engineering that mirrors Claude Code behavior

### Key Design Patterns

**Tool Architecture**: Each tool is implemented as a `@tool` decorated function with comprehensive docstrings that serve as both documentation and prompt engineering. The tool descriptions are critical - they are described as "MASTER PIECES of prompt engineering" and should not be modified unless there's a specific bug.

**Background Process Management**: Global tracking system (`_background_shells`) for managing long-running bash processes with cancellation support via Esc key or Ctrl+C.

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

Required:
- `ANTHROPIC_API_KEY`: Get from https://console.anthropic.com/

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
- `/init`: Analyze codebase and create/update CLAUDE.md
- `Ctrl+C` or `Esc`: Cancel long-running tool execution

## Reverse Engineering Documentation

The `docs/` directory contains extracted Claude Code system prompts and tool descriptions from API interception using Proxyman. The `data/` directory contains sample API requests/responses. These serve as reference for maintaining fidelity to original Claude Code behavior.

## Example Projects

The `example_projects/` directory contains generated projects (caro game, expense trackers) that demonstrate the agent's capabilities. These are excluded from git via `.gitignore`.
# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.

      
      IMPORTANT: this context may or may not be relevant to your tasks. You should not respond to this context unless it is highly relevant to your task.
</system-reminder>