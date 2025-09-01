"""Web fetch tool implementation for retrieving and analyzing web content."""

import os
import requests
from typing import Optional
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from bs4 import BeautifulSoup
import html2text
from urllib.parse import urlparse
import hashlib
import json
import time
from pathlib import Path


class WebFetchCache:
    """Simple file-based cache for web fetch results."""

    def __init__(self, cache_dir: str = "/tmp/webfetch_cache", ttl_minutes: int = 15):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = ttl_minutes * 60

    def _get_cache_key(self, url: str, prompt: str) -> str:
        """Generate cache key from URL and prompt."""
        combined = f"{url}|{prompt}"
        return hashlib.sha256(combined.encode()).hexdigest()

    def get(self, url: str, prompt: str) -> Optional[str]:
        """Get cached result if exists and not expired."""
        cache_key = self._get_cache_key(url, prompt)
        cache_file = self.cache_dir / f"{cache_key}.json"

        if cache_file.exists():
            try:
                with open(cache_file, "r") as f:
                    data = json.load(f)

                # Check if cache is expired
                if time.time() - data["timestamp"] < self.ttl_seconds:
                    return data["result"]
                else:
                    # Clean up expired cache
                    cache_file.unlink()
            except (json.JSONDecodeError, KeyError):
                # Invalid cache file, remove it
                cache_file.unlink()

        return None

    def set(self, url: str, prompt: str, result: str):
        """Store result in cache."""
        cache_key = self._get_cache_key(url, prompt)
        cache_file = self.cache_dir / f"{cache_key}.json"

        data = {
            "url": url,
            "prompt": prompt,
            "result": result,
            "timestamp": time.time(),
        }

        with open(cache_file, "w") as f:
            json.dump(data, f)

    def clean_expired(self):
        """Remove expired cache files."""
        current_time = time.time()
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, "r") as f:
                    data = json.load(f)
                    if current_time - data["timestamp"] >= self.ttl_seconds:
                        cache_file.unlink()
            except (json.JSONDecodeError, KeyError):
                # Invalid cache file, remove it
                cache_file.unlink()


class WebFetchLLM:
    """Singleton class for managing the web fetch LLM instance."""

    _instance = None
    _llm = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_llm(self):
        """Get or create the LLM instance for web content processing."""
        if self._llm is None:
            # Use DeepSeek for web content processing
            deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
            if not deepseek_api_key:
                raise ValueError("DEEPSEEK_API_KEY environment variable is required")

            self._llm = ChatOpenAI(
                api_key=deepseek_api_key,
                base_url="https://api.deepseek.com",
                model="deepseek-chat",  # DeepSeek model for content processing
            )
        return self._llm

    def reset(self):
        """Reset the LLM instance."""
        self._llm = None


# Create singleton instances
web_fetch_llm = WebFetchLLM()
web_fetch_cache = WebFetchCache()


@tool
def web_fetch(url: str, prompt: str) -> str:
    """
    - Fetches content from a specified URL and processes it using an AI model
    - Takes a URL and a prompt as input
    - Fetches the URL content, converts HTML to markdown
    - Processes the content with the prompt using a small, fast model
    - Returns the model's response about the content
    - Use this tool when you need to retrieve and analyze web content

    Usage notes:
      - IMPORTANT: If an MCP-provided web fetch tool is available, prefer using that tool instead of this one, as it may have fewer restrictions. All MCP-provided tools start with "mcp__".
      - The URL must be a fully-formed valid URL
      - HTTP URLs will be automatically upgraded to HTTPS
      - The prompt should describe what information you want to extract from the page
      - This tool is read-only and does not modify any files
      - Results may be summarized if the content is very large
      - Includes a self-cleaning 15-minute cache for faster responses when repeatedly accessing the same URL
      - When a URL redirects to a different host, the tool will inform you and provide the redirect URL in a special format. You should then make a new WebFetch request with the redirect URL to fetch the content.
    """
    try:
        # Clean expired cache entries periodically
        web_fetch_cache.clean_expired()

        # Check cache first
        cached_result = web_fetch_cache.get(url, prompt)
        if cached_result:
            return f"[CACHED] {cached_result}"

        # Upgrade HTTP to HTTPS
        parsed_url = urlparse(url)
        if parsed_url.scheme == "http":
            url = url.replace("http://", "https://", 1)

        # Validate URL format
        if not parsed_url.scheme or not parsed_url.netloc:
            return "Error: Invalid URL format. Please provide a fully-formed URL like https://example.com"

        # Fetch the content
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }

        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)

        # Check for redirects to different host
        if response.history:
            final_url = response.url
            final_host = urlparse(final_url).netloc
            original_host = parsed_url.netloc

            if final_host != original_host:
                return (
                    f"Redirect detected to different host.\n"
                    f"Original: {url}\n"
                    f"Redirect: {final_url}\n"
                    f"Please make a new WebFetch request with the redirect URL."
                )

        response.raise_for_status()

        # Convert HTML to markdown
        content_type = response.headers.get("content-type", "").lower()

        if "text/html" in content_type:
            # Parse HTML and convert to markdown
            soup = BeautifulSoup(response.text, "html.parser")

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Convert to markdown
            h = html2text.HTML2Text()
            h.ignore_links = False
            h.ignore_images = False
            h.body_width = 0  # Don't wrap lines

            markdown_content = h.handle(str(soup))

        elif "text/" in content_type or "json" in content_type:
            # Plain text or JSON, use as-is
            markdown_content = response.text
        else:
            return f"Error: Unsupported content type: {content_type}"

        # Truncate if too large (over 50k characters)
        if len(markdown_content) > 50000:
            markdown_content = (
                markdown_content[:50000] + "\n\n[Content truncated due to size...]"
            )

        # Process with LLM
        llm = web_fetch_llm.get_llm()

        # Create the processing prompt
        processing_prompt = f"""
You are analyzing web content. Please process the following content according to the user's request.

User's request: {prompt}

Web content from {url}:

{markdown_content}

Please provide a concise and relevant response based on the user's request.
"""

        # Get LLM response
        response = llm.invoke(processing_prompt)

        # Extract the content
        if hasattr(response, "content"):
            result = response.content
        else:
            result = str(response)

        # Cache the result
        web_fetch_cache.set(url, prompt, result)

        return result

    except requests.exceptions.RequestException as e:
        return f"Error fetching URL: {str(e)}"
    except Exception as e:
        return f"Error processing web content: {str(e)}"


# Export the tool
__all__ = ["web_fetch", "web_fetch_llm", "web_fetch_cache"]
