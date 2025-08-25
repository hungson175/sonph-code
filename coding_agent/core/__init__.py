"""Core components of the coding agent."""

from .agent import CodingAgent
from .config import config
from .shell_manager import shell_manager

__all__ = ["CodingAgent", "config", "shell_manager"]
