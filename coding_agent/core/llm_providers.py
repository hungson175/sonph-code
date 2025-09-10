"""LLM provider abstraction for multiple models."""

import os
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_xai import ChatXAI
from langchain_core.messages import BaseMessage
from langchain_core.tools import BaseTool


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(
        self, model_name: str, temperature: float = 0.0, max_tokens: int = 16384
    ):
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.llm = self._create_llm()

    @abstractmethod
    def _create_llm(self):
        """Create the LLM instance."""
        pass

    @abstractmethod
    def bind_tools(self, tools: List[BaseTool]):
        """Bind tools to the LLM."""
        pass

    @abstractmethod
    def create_cached_message(self, content: str):
        """Create a message with appropriate caching."""
        pass

    @abstractmethod
    def remove_cache_control(self, message: BaseMessage):
        """Remove cache control from message if applicable."""
        pass

    @abstractmethod
    def format_usage_info(self, response_metadata: Dict[str, Any]) -> str:
        """Format token usage information for display."""
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Get the provider name for display."""
        pass


class ClaudeProvider(LLMProvider):
    """Claude/Anthropic provider with manual cache control."""

    def __init__(self, model_name: str = "claude-sonnet-4-20250514", **kwargs):
        # Validate API key
        if not os.getenv("ANTHROPIC_API_KEY"):
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        super().__init__(model_name, **kwargs)

    def _create_llm(self):
        """Create Claude LLM instance."""
        return ChatAnthropic(
            model=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

    def bind_tools(self, tools: List[BaseTool]):
        """Bind tools to Claude LLM."""
        return self.llm.bind_tools(tools)

    def create_cached_message(self, content: str):
        """Create a message with cache control for Claude."""
        return [
            {"type": "text", "text": content, "cache_control": {"type": "ephemeral"}}
        ]

    def remove_cache_control(self, message: BaseMessage):
        """Remove cache control from message for reuse."""
        if hasattr(message, "content") and isinstance(message.content, list):
            if len(message.content) > 0 and isinstance(message.content[0], dict):
                message.content[0].pop("cache_control", None)

    def format_usage_info(self, response_metadata: Dict[str, Any]) -> str:
        """Format Claude token usage information."""
        usage = response_metadata.get("usage", {})
        input_tokens = usage.get("input_tokens", 0)
        cached_tokens = usage.get("cache_read_input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)

        return (
            f"📊 Tokens - Input: {input_tokens} "
            f"(cached: {cached_tokens}) Output: {output_tokens}"
        )

    @property
    def provider_name(self) -> str:
        return "Claude"


class DeepSeekProvider(LLMProvider):
    """DeepSeek provider with auto-cache management."""

    def __init__(self, model_name: str = "deepseek-chat", **kwargs):
        # Validate API key
        if not os.getenv("DEEPSEEK_API_KEY"):
            raise ValueError("DEEPSEEK_API_KEY environment variable is required")
        super().__init__(model_name, **kwargs)

    def _create_llm(self):
        """Create DeepSeek LLM instance."""
        return ChatOpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com",
            model=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

    def bind_tools(self, tools: List[BaseTool]):
        """Bind tools to DeepSeek LLM."""
        return self.llm.bind_tools(tools)

    def create_cached_message(self, content: str):
        """DeepSeek handles caching automatically, return plain content."""
        return content

    def remove_cache_control(self, message: BaseMessage):
        """No-op for DeepSeek (auto-cache management)."""
        pass

    def format_usage_info(self, response_metadata: Dict[str, Any]) -> str:
        """Format DeepSeek token usage information."""
        usage = response_metadata.get("usage", {})
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)

        return f"📊 Tokens - Input: {input_tokens} Output: {output_tokens}"

    @property
    def provider_name(self) -> str:
        return "DeepSeek"


class GrokProvider(LLMProvider):
    """Grok/xAI provider with auto-cache management."""

    def __init__(self, model_name: str = "grok-code-fast-1", **kwargs):
        # Validate API key
        if not os.getenv("XAI_API_KEY"):
            raise ValueError("XAI_API_KEY environment variable is required")
        super().__init__(model_name, **kwargs)

    def _create_llm(self):
        """Create Grok LLM instance."""
        return ChatXAI(
            model=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

    def bind_tools(self, tools: List[BaseTool]):
        """Bind tools to Grok LLM."""
        return self.llm.bind_tools(tools)

    def create_cached_message(self, content: str):
        """Grok handles caching automatically, return plain content."""
        return content

    def remove_cache_control(self, message: BaseMessage):
        """No-op for Grok (auto-cache management)."""
        pass

    def format_usage_info(self, response_metadata: Dict[str, Any]) -> str:
        """Format Grok token usage information."""
        usage = response_metadata.get("usage", {})
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)

        return f"📊 Tokens - Input: {input_tokens} Output: {output_tokens}"

    @property
    def provider_name(self) -> str:
        return "Grok"


class LLMProviderFactory:
    """Factory for creating LLM providers."""

    _providers = {
        "claude": ClaudeProvider,
        "sonnet": ClaudeProvider,  # Alias for Claude
        "deepseek": DeepSeekProvider,
        "ds": DeepSeekProvider,  # Alias for DeepSeek
        "grok": GrokProvider,
        "xai": GrokProvider,  # Alias for Grok
    }

    @classmethod
    def create_provider(cls, provider_name: str, **kwargs) -> LLMProvider:
        """Create a provider by name."""
        provider_name = provider_name.lower()

        if provider_name not in cls._providers:
            available = ", ".join(cls._providers.keys())
            raise ValueError(
                f"Unknown provider '{provider_name}'. Available: {available}"
            )

        provider_class = cls._providers[provider_name]
        return provider_class(**kwargs)

    @classmethod
    def get_available_providers(cls) -> List[str]:
        """Get list of available provider names."""
        return list(cls._providers.keys())

    @classmethod
    def get_default_provider(cls) -> str:
        """Get the default provider name."""
        return "sonnet"
