# Sonph-Code Global Launcher

This directory contains scripts to run `sonph-code` from anywhere on your system.

## Installation

### Option 1: Global Installation (Recommended)
```bash
sudo ./install.sh
```
This creates a symlink in `/usr/local/bin/sonph-code` so you can run `sonph-code` from anywhere.

### Option 2: Add to PATH
Add this to your `~/.bashrc` or `~/.zshrc`:
```bash
export PATH="/Users/sonph36/dev/demo/sonph-code:$PATH"
```

### Option 3: Create Alias
Add this to your `~/.bashrc` or `~/.zshrc`:
```bash
alias sonph-code="/Users/sonph36/dev/demo/sonph-code/sonph-code.sh"
```

## Usage

After installation, you can run `sonph-code` from any directory:

```bash
# Run in current directory
sonph-code

# Run in specific directory
sonph-code /path/to/your/project

# Show help
sonph-code --help
```

## Features

- 🚀 Launch from any directory
- 📁 Automatically sets working directory to where you run it
- 🔧 Uses `uv` to manage Python environment
- 🤖 Full access to all customized agents
- 💡 Same functionality as running `uv run python main.py`

## Files

- `sonph-code.sh` - Main launcher script (bash)
- `sonph-code` - Python launcher script (alternative)
- `install.sh` - Installation script for global access
- `LAUNCHER_README.md` - This file

## How It Works

1. When you run `sonph-code /some/project`, the script:
2. Changes to that directory
3. Sets `INITIAL_DIR` environment variable
4. Runs the main.py using `uv run python main.py`
5. The main.py detects `INITIAL_DIR` and sets it as working directory

This ensures the Claude Code agent works in the directory where you invoked it, regardless of where the code is installed.