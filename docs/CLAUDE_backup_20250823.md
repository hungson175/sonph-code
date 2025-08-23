# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based coding agent that replicates Claude Code functionality using LangChain and Anthropic's API. The project demonstrates reverse engineering of Claude Code through API interception and reimplementation of essential coding tools.

## Development Commands

### Environment Setup
```bash
# Install dependencies (recommended)
uv sync

# Alternative with pip
pip install -e .

# Set up environment variables
cp .env.example .env
# Edit .env with your ANTHROPIC_API_KEY and optional LANGSMITH_* keys
```

### Running the Application
```bash
# Primary way to run the agent
uv run python coding_agent.py

# With activated virtual environment
source .venv/bin/activate
python coding_agent.py
```

### Development Tools
```bash
# Code formatting
black coding_agent.py

# Linting
ruff check coding_agent.py

# Testing
pytest
```

## Architecture

### Core Components

- **`coding_agent.py`**: Main application file containing the complete agent implementation
- **Tool System**: Implements essential coding tools (Read, Write, Edit, Bash, Grep, etc.) with exact Claude Code functionality
- **Background Shell Management**: Handles long-running processes with cancellation support
- **TodoWrite System**: Sophisticated task management tool (considered the "heart" of Claude Code)

### Key Dependencies

- **LangChain + Anthropic**: Core LLM integration using `claude-sonnet-4-20250514`
- **ripgrep**: Required external dependency for search functionality
- **colorama**: Terminal output formatting
- **python-dotenv**: Environment variable management

### Tool Implementation

The agent implements these essential tools with Claude Code-compatible interfaces:
- File operations: Read, Write, Edit, MultiEdit
- Directory operations: LS, Glob, Grep  
- Command execution: Bash, BashOutput
- Task management: TodoWrite
- Search & analysis capabilities

### Critical Implementation Notes

- Tool descriptions are "master pieces of prompt engineering" - never modify unless fixing specific bugs
- TodoWrite is the most sophisticated tool requiring careful implementation
- Background shell system supports process cancellation via Esc key
- All tools maintain exact compatibility with Claude Code specifications

## Project Structure

- `/docs/claude-code/`: Contains extracted tool descriptions and system prompts from original Claude Code
- `/data/`: API request samples and analysis from reverse engineering process
- `/example_projects/`: Sample applications (caro game, expense trackers) for testing
- `expense-tracker-prompt.txt`: Example prompt for creating NextJS expense tracking app

## Environment Requirements

- Python 3.11+
- ripgrep (brew install ripgrep / apt install ripgrep)
- Anthropic API key
- Optional: LangSmith API key for tracing

## Usage Patterns

The agent supports interactive coding assistance including:
- File operations and code analysis
- Command execution with background process support
- Project scaffolding and implementation
- Multi-language development (NextJS/React, Python, etc.)
- Task planning and management via TodoWrite

Example prompts are provided in README.md for testing various capabilities.