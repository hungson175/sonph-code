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

2. **Set up API keys:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys:
   # - ANTHROPIC_API_KEY (required for Claude - default provider)
   # - DEEPSEEK_API_KEY (optional for DeepSeek provider)  
   # - XAI_API_KEY (optional for Grok provider)
   ```

3. **Run the agent:**
   ```bash
   # Using global launcher (easiest)
   sonph-code                  # Run in current directory
   sonph-code /path/to/project # Run in specific directory
   sonph-code --llm deepseek   # Use DeepSeek provider
   sonph-code --llm grok       # Use Grok provider
   
   # Alternative: Direct Python execution (harder to use)
   uv run python main.py
   ```

## Example Prompts

Here are some example prompts to try with the coding agent:

- Tạo game cờ caro (5 quân thẳng hàng/chéo, không phải tic-tac-toe) cho web sử dụng NextJS/ReactJS với thiết kế tối giản cho 2 người chơi, màu đen trắng - trông như kiểu cờ vây ấy
- Create a chess game for 2 players (human vs human, human vs computer - use some quick & good js chess engine - search if you needed to ) using NextJS/React with minimalist black/white design, beautiful and clear graphics, implementing all chess rules (winning conditions, castling, etc.) - use image or something nice for chess figure, not just font 
- Read file expense-tracker-prompt.txt then implement the application

## License

This project is for educational and demonstration purposes.
