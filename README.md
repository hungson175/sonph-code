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
   # Add your DEEPSEEK_API_KEY from https://platform.deepseek.com/
   ```

3. **Run the agent:**
   ```bash
   # Method 1: Using uv (recommended)
   uv run python main.py
   
   # Method 2: Using the run script
   ./run.sh
   
   # Method 3: Activate venv first
   source .venv/bin/activate
   python main.py
   ```
   
   **Important:** Do NOT run `python main.py` directly without uv or activating the virtual environment, as dependencies won't be available.

## Example Prompts

Here are some example prompts to try with the coding agent:

- Tạo game cờ caro (5 quân thẳng hàng/chéo, không phải tic-tac-toe) cho web sử dụng NextJS/ReactJS với thiết kế tối giản cho 2 người chơi, màu đen trắng - trông như kiểu cờ vây ấy
- Create a chess game for 2 players (human vs human, human vs computer - use stockfish - search if you needed to ) using NextJS/React with minimalist black/white design, beautiful and clear graphics, implementing all chess rules (winning conditions, castling, etc.) 
- Read file expense-tracker-prompt.txt then implement the application

## License

This project is for educational and demonstration purposes.
