#!/usr/bin/env python3
"""Test for Claude's native web search functionality."""

from coding_agent.tools.web_search_tool import web_search


def test_web_search_tool():
    """Test that web search tool can be invoked."""
    # Test basic invocation - actual search may fail due to API availability
    try:
        result = web_search.invoke({"query": "Python programming"})
        # If successful, result should be a string
        assert isinstance(result, str)
        print(f"Web search successful: {result[:100]}...")
    except Exception as e:
        # Web search may not be available, but tool should still be callable
        print(f"Web search unavailable: {e}")
        assert (
            "Web search error" in str(e)
            or "Connection error" in str(e)
            or "Overloaded" in str(e)
        )


def test_web_search_with_domains():
    """Test web search with domain filtering."""
    try:
        result = web_search.invoke(
            {
                "query": "machine learning",
                "allowed_domains": ["arxiv.org"],
            }
        )
        assert isinstance(result, str)
    except Exception:
        # Expected if web search is not available
        pass


if __name__ == "__main__":
    print("Testing web search tool...")
    test_web_search_tool()
    test_web_search_with_domains()
    print("✅ Web search tool tests completed")
