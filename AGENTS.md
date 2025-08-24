# Coding Agent AGENTS.md

## Project Overview
This is a Python-based coding agent that replicates Claude Code functionality using LangChain and Anthropic's API. The project demonstrates reverse engineering of Claude Code through API interception and reimplementation of essential coding tools.

## Development Environment Setup
- **Python version**: 3.9+
- **Package manager**: Use `uv` (preferred over pip)
- **Install dependencies**: `uv sync`
- **Run agent**: `uv run python main.py`
- **Required external tools**: 
  - ripgrep (rg): `brew install ripgrep` (macOS) or `sudo apt install ripgrep` (Linux)

## Environment Configuration
Required:
- `ANTHROPIC_API_KEY`: Get from https://console.anthropic.com/

Optional (for tracing):
- `LANGSMITH_TRACING=true`
- `LANGSMITH_API_KEY`: Get from https://smith.langchain.com/
- `LANGSMITH_PROJECT`: Your project name

## Code Style Guidelines
- **Formatter**: Use Black (`uv run black .`)
- **Linter**: Use Ruff (`uv run ruff check .` or `uv run ruff check . --fix`)
- **Architecture**: Modular package structure under `coding_agent/`
- **Tool descriptions**: Critical for prompt engineering - do not modify unless fixing specific bugs
- **Import organization**: Follow standard Python conventions

## Testing Instructions
- **Run tests**: `uv run pytest`
- **LLM-related code**: Do not create automated tests (costly)
- **Coverage**: Ensure non-LLM code has adequate test coverage
- **Test structure**: Place tests in `tests/` directory

## Development Workflow
- **Feature branches**: Create from `main` with pattern `feature_<short_name>`
- **Before committing**: 
  - Write tests for all code
  - Run linting: `uv run ruff check .`
  - Format code: `uv run black .`
  - Ensure all tests pass
  - No basic compilation errors allowed
- **File organization**: 
  - Documentation in `docs/`
  - Tests in `tests/`
  - Sample code in `sample_codes/` (reference only)

## Architecture Notes
- **Core entry point**: `main.py`
- **Modular structure**: `coding_agent/` package with `core/`, `tools/`, `commands/`, `utils/`
- **Tool pattern**: Each tool uses `@tool` decorator with comprehensive docstrings
- **Background processes**: Managed via `BackgroundShellManager` with cancellation support
- **Caching**: Uses Anthropic's ephemeral caching for optimization
- **Message flow**: SystemMessage + HumanMessage + ToolMessage pattern

## Interactive Commands
Within the agent CLI:
- `quit`/`exit`: Exit the agent
- `reset`: Reset conversation history
- `pwd`/`cd <path>`: Directory navigation
- `/init`: Analyze codebase and update CLAUDE.md
- `/commands`: List available commands
- `/memory`: View current context
- `Ctrl+C`/`Esc`: Cancel long-running operations

## Dependencies
Core packages:
- `langchain-anthropic`: LLM integration
- `langchain-core`: Tool abstractions
- `python-dotenv`: Environment management
- `colorama`: Terminal colors

Development packages:
- `pytest`: Testing framework
- `black`: Code formatter
- `ruff`: Fast Python linter

## Important Notes
- Tool descriptions are "MASTER PIECES of prompt engineering" - handle with care
- Preserve original Claude Code behavior fidelity
- Background process management supports cancellation
- Conversation history maintained with proper message patterns