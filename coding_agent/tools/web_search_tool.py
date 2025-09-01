"""Web search tool implementation using Claude's built-in web search."""

from typing import Optional, List
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
import os
from ..core.config import Config


class WebSearchLLM:
    """Singleton class for managing the web search LLM instance."""

    _instance = None
    _llm = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_llm(self):
        """Get or create the LLM instance."""
        if self._llm is None:
            deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
            if not deepseek_api_key:
                raise ValueError("DEEPSEEK_API_KEY environment variable is required")

            self._llm = ChatOpenAI(
                api_key=deepseek_api_key,
                base_url="https://api.deepseek.com",
                model=Config.MODEL_NAME,  # Use config model name
            )
        return self._llm

    def reset(self):
        """Reset the LLM instance (useful for testing or config changes)."""
        self._llm = None


# Create singleton instance
web_search_llm = WebSearchLLM()


@tool
def web_search(
    query: str,
    allowed_domains: Optional[List[str]] = None,
    blocked_domains: Optional[List[str]] = None,
) -> str:
    """
    - Allows Claude to search the web and use the results to inform responses
    - Provides up-to-date information for current events and recent data
    - Returns search result information formatted as search result blocks
    - Use this tool for accessing information beyond Claude's knowledge cutoff
    - Searches are performed automatically within a single API call

    Usage notes:
      - Domain filtering is supported to include or block specific websites
      - Web search is only available in the US
      - Account for "Today's date" in <env>. For example, if <env> says "Today's date: 2025-07-01", and the user wants the latest docs, do not use 2024 in the search query. Use 2025.
    """
    try:
        # Get singleton LLM instance
        llm = web_search_llm.get_llm()

        # Configure web search tool - using the format from langchain-anthropic docs
        web_search_config = {
            "type": "web_search_20250305",  # The actual type identifier for Claude's web search
            "name": "web_search",
            "max_uses": 5,  # Default number of searches
        }

        # Add domain filters if provided
        if allowed_domains:
            web_search_config["allowed_domains"] = allowed_domains
        if blocked_domains:
            web_search_config["blocked_domains"] = blocked_domains

        # Bind the web search tool to Claude
        llm_with_search = llm.bind_tools([web_search_config])

        # Execute the search query
        response = llm_with_search.invoke(query)

        # Return the search results
        if hasattr(response, "content"):
            return response.content
        else:
            return str(response)

    except Exception as e:
        # If web search isn't available, return error message
        return f"Web search error: {str(e)}. Ensure web search is enabled for your API key."


# Export the tool
__all__ = ["web_search", "web_search_llm"]
