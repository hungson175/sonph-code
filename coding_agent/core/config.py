"""Configuration management for the coding agent."""

import os
from dotenv import load_dotenv


class Config:
    """Centralized configuration management."""

    # Model and API settings
    MODEL_NAME = "deepseek-chat"  # Default DeepSeek model

    # Timing settings
    CACHE_DURATION_SECONDS = 60
    KEYBOARD_POLL_INTERVAL = 0.1
    BACKGROUND_SHELL_TIMEOUT_MS = 120000  # 2 minutes in milliseconds

    # UI and display settings
    ESC_KEY_CODE = 27
    DEFAULT_READ_LIMIT = 2000
    MAX_OUTPUT_LENGTH = 30000

    def __init__(self):
        load_dotenv()
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        if not self.deepseek_api_key:
            raise ValueError("DEEPSEEK_API_KEY environment variable is required")

        self.langsmith_tracing = (
            os.getenv("LANGSMITH_TRACING", "false").lower() == "true"
        )
        self.langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
        self.langsmith_project = os.getenv("LANGSMITH_PROJECT", "coding-agent")


# Global configuration instance
config = Config()
