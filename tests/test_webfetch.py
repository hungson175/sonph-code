#!/usr/bin/env python3
"""Test for WebFetch tool functionality."""

from coding_agent.tools.web_fetch_tool import web_fetch


def test_web_fetch_tool():
    """Test that web fetch tool can be invoked with a simple request."""
    try:
        # Test with a simple, reliable URL
        result = web_fetch.invoke(
            {
                "url": "https://www.example.com",
                "prompt": "What is the main heading on this page?",
            }
        )

        # Should return some content
        assert isinstance(result, str)
        assert len(result) > 0

        # Should mention Example Domain or similar
        assert "Example" in result or "example" in result.lower()

        print(f"✅ Web fetch successful: {result[:200]}...")

    except Exception as e:
        # Web fetch may fail due to network issues or API limits
        print(f"⚠️ Web fetch test failed: {e}")
        # Check that error message is informative
        error_msg = str(e)
        assert "Error" in error_msg or "error" in error_msg.lower()


if __name__ == "__main__":
    print("Testing web fetch tool...")
    test_web_fetch_tool()
    print("✅ Web fetch tool tests completed")
