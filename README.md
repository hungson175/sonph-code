# sonph-code

> AI coding assistant - write, edit, and manage code through natural language

## 🚀 Quick Start

**Prerequisites:**
- Python 3.11+
- [Grok API key](https://console.x.ai/) (**required**)

**Install:**

```bash
# 1. Install dependencies
brew install ripgrep  # macOS
# sudo apt install ripgrep  # Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Clone and setup

git clone https://github.com/hungson175/sonph-code.git

cd sonph-code
uv sync

# 3. Configure API key
cp .env.example .env
# Edit .env: XAI_API_KEY=xai-your-key-here

# 4. Install globally (optional)
./install.sh
```

**Run:**
```bash
sonph-code  # if installed globally
# OR
uv run python main.py
```

## 💡 Usage

Just type what you want in natural language:

```
> Create a REST API for user authentication with JWT tokens
> Add error handling to payment.py
> Refactor this code to use dependency injection
```

### Example Prompts

**Vietnamese (Cờ Caro game):**
```
Tạo game cờ caro (5 quân thẳng hàng/chéo, không phải tic-tac-toe) cho web sử dụng NextJS/ReactJS với thiết kế tối giản cho 2 người chơi, màu đen trắng - trông như kiểu cờ vây ấy. 2D với shadow đẹp đẹp tí, nhưng vẫn phải simple và elegant nhá ! Tạo thư mục để làm version mới hoàn toàn nhá !
```

**English (Chess game):**
```
Create a chess game for 2 players (human vs human) using NextJS/React with minimalist black/white design, beautiful and clear graphics, implementing all chess rules (winning conditions, castling, etc.) - use image or something nice for chess figure, not just font
```

**Implementation from spec:**
```
Read file expense-tracker-prompt.txt then implement the application
```

### Commands

- `/model` - Switch AI provider (claude/deepseek/grok)
- `/init` - Analyze codebase
- `reset` - Clear history
- `quit` - Exit

## 🤖 AI Providers

| Provider | API Key | Required? |
|----------|---------|-----------|
| **Grok** ⭐ | `XAI_API_KEY` | **Yes** |
| Claude | `ANTHROPIC_API_KEY` | Optional |
| DeepSeek | `DEEPSEEK_API_KEY` | Optional |

Switch providers: `/model claude` or `/model deepseek`

## 📚 More Info

- Development: See [CLAUDE.md](CLAUDE.md)
- Run in directory: `sonph-code /path/to/project`

---

Inspired by [Claude Code](https://claude.com/claude-code)
