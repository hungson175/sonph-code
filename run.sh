#!/bin/bash
# Run the Sonph-Code agent with proper environment

# Use uv to run with the correct virtual environment
uv run python main.py "$@"