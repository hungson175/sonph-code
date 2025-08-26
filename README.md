# Coding Agent - Claude Code Implementation

A Python-based coding agent that replicates Claude Code functionality using LangChain and Anthropic's API.

## Quick Start

1. **Install dependencies:**
   ```bash
   # Install ripgrep (required)
   brew install ripgrep  # macOS
   # sudo apt install ripgrep  # Linux
   
   # Install Python dependencies
   uv sync
   ```

2. **Set up API key:**
   ```bash
   cp .env.example .env
   # Add your ANTHROPIC_API_KEY from https://console.anthropic.com/
   ```

3. **Run the agent:**
   ```bash
   uv run python main.py
   ```

## Example Prompts

Here are some example prompts to try with the coding agent:

- Tạo game cờ caro (5 quân thẳng hàng/chéo, không phải tic-tac-toe) cho web sử dụng NextJS/ReactJS với thiết kế tối giản cho 2 người chơi, màu đen trắng
- Create a chess game for 2 players (human vs human, human vs computer - use stockfish - search if you needed to ) using NextJS/React with minimalist black/white design, beautiful and clear graphics, implementing all chess rules (winning conditions, castling, etc.) 
- Read file expense-tracker-prompt.txt then implement the application

## License

This project is for educational and demonstration purposes.
