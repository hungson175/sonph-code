# Coding Agent - Claude Code Implementation

A Python-based coding agent that replicates Claude Code functionality using LangChain and Anthropic's API.

## Overview

This project demonstrates how to reverse engineer and implement a Claude Code-like assistant with essential coding tools. The agent provides interactive assistance for software development tasks including file operations, code analysis, command execution, and project management.

## Reverse Engineering Process

The original Claude Code functionality was analyzed through:
- Using Proxyman to intercept requests/responses to Anthropic API endpoints → example: `data/api_request_sample.json`
- Extracting system prompts and tool descriptions → stored in `./docs/`
- Self-implementing the agent and tools

**Note:** Tool implementation is straightforward except for TodoWrite, which is the heart of claude-code with a sophisticated/elegant implementation - consider it a learning exercise!

## Installation

### Prerequisites
- Python 3.11 or higher
- [uv](https://docs.astral.sh/uv/) (recommended)
- [ripgrep](https://github.com/BurntSushi/ripgrep) - Required for search functionality

### Setup

1. **Clone and navigate to the project:**
   ```bash
   git clone <repository-url>
   cd sonph-code
   ```

2. **Install ripgrep (required for search functionality):**
   ```bash
   # macOS
   brew install ripgrep
   
   # Ubuntu/Debian
   sudo apt install ripgrep
   
   # Windows
   winget install BurntSushi.ripgrep.MSVC
   
   # Or download from: https://github.com/BurntSushi/ripgrep/releases
   ```

3. **Install dependencies using uv (recommended):**
   ```bash
   uv sync
   ```

4. **Set up environment variables:**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env and add your API keys:
   # - Get Anthropic API key from: https://console.anthropic.com/
   # - Get LangSmith API key from: https://smith.langchain.com/ (optional)
   ```

## Usage

### Running the Agent

```bash
# Using uv (recommended)
uv run python coding_agent.py

# Or with activated virtual environment
source .venv/bin/activate  # Unix/macOS
python coding_agent.py
```

The agent starts in interactive mode where you can:
- Ask coding questions
- Request file operations
- Execute commands
- Manage projects
- Get assistance with debugging and refactoring

### Available Tools

The agent includes these essential coding tools:
- **File Operations:** Read, Write, Edit, MultiEdit
- **Directory Operations:** LS, Glob, Grep
- **Command Execution:** Bash, BashOutput
- **Task Management:** TodoWrite
- **Search & Analysis:** Pattern matching, content search

## Example Prompts

Here are some example prompts to try with the coding agent:

- Tạo game cờ caro (5 quân thẳng hàng/chéo, không phải tic-tac-toe) cho web sử dụng NextJS/ReactJS với thiết kế tối giản cho 2 người chơi, màu đen trắng
- Create a chess game for 2 players using NextJS/React with minimalist black/white design, beautiful and clear graphics, implementing all chess rules (winning conditions, castling, etc.)
- Read file expense-tracker-prompt.txt then implement the application

## License

This project is for educational and demonstration purposes.
