# sonph-code

> An AI-powered coding assistant that helps you write, edit, and manage code through natural language conversations.

## 🚀 Quick Start

### Prerequisites

You'll need:
- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) (Python package manager)
- [ripgrep](https://github.com/BurntSushi/ripgrep) (for code search)
- **Grok API key** from [console.x.ai](https://console.x.ai/)

### Installation

1. **Install system dependencies:**

   ```bash
   # macOS
   brew install ripgrep

   # Ubuntu/Debian
   sudo apt install ripgrep

   # Install uv (if not already installed)
   curl -LsSf https://astral.sh/uv/install.sh | sh
   # Note: You may need to restart your shell or run: source ~/.local/bin/env
   ```

2. **Clone and setup:**

   ```bash
   git clone <your-repo-url>
   cd sonph-code

   # Install Python dependencies
   uv sync
   ```

3. **Configure your API key:**

   ```bash
   cp .env.example .env
   # Edit .env and add your Grok API key:
   # XAI_API_KEY=xai-your-key-here
   ```

4. **Install globally (optional but recommended):**

   ```bash
   ./install.sh
   # If permission denied, run: sudo ./install.sh
   ```

### First Run

```bash
# If installed globally:
sonph-code

# Or run directly:
uv run python main.py
```

That's it! The assistant will start and you can begin chatting.

## 💡 How to Use

### Basic Usage

Simply type what you want to do in natural language:

```
> Create a Python function to calculate fibonacci numbers

> Add error handling to the login function in auth.py

> Refactor this code to use async/await

> Write tests for the User model
```

### Switching Models

By default, sonph-code uses **Grok** (fast and cost-effective). You can switch to other providers:

1. Add the API key to `.env`:
   - `ANTHROPIC_API_KEY` for Claude
   - `DEEPSEEK_API_KEY` for DeepSeek

2. Use the `/model` command:
   ```
   > /model claude
   > /model deepseek
   > /model grok
   ```

### Useful Commands

- `/model` - Switch between AI providers
- `/init` - Analyze your codebase and create CLAUDE.md
- `/commands` - Show all available commands
- `reset` - Clear conversation history
- `quit` or `exit` - Exit the assistant
- `Ctrl+C` or `Esc` - Cancel running operations

### Example Prompts

**Creating new features:**
```
> Create a REST API endpoint for user registration with email validation
```

**Code analysis:**
```
> Analyze this codebase and suggest performance improvements
```

**Refactoring:**
```
> Refactor the authentication module to follow SOLID principles
```

**Bug fixing:**
```
> Fix the memory leak in the WebSocket connection handler
```

## 🤖 Supported AI Providers

| Provider | Speed | Cost | API Key Required |
|----------|-------|------|------------------|
| **Grok/xAI** (Default) ⭐ | Fast | Low | `XAI_API_KEY` - **REQUIRED** |
| Claude/Anthropic | Medium | Medium | `ANTHROPIC_API_KEY` - Optional |
| DeepSeek | Fast | Very Low | `DEEPSEEK_API_KEY` - Optional |

**Note:** You must have at least the Grok API key configured. Other providers are optional.

## 🛠️ Advanced Usage

### Run in a Specific Directory

```bash
sonph-code /path/to/your/project
```

### Run Without Global Installation

```bash
cd /path/to/sonph-code
uv run python main.py
```

### Development Mode

For development and contributing, see [CLAUDE.md](CLAUDE.md) for:
- Architecture details
- Tool implementations
- Development commands
- Code quality guidelines

## 📝 License

This project is for educational and demonstration purposes.

## 🙏 Credits

Inspired by Claude Code from Anthropic.
