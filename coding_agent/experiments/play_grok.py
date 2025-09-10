"""
Simple Grok integration using LangChain

This script demonstrates the most basic usage of Grok with LangChain:
1. Send a simple message "Hello ! I am Son"
2. Get response from Grok

Requirements:
- pip install langchain-xai
- Set XAI_API_KEY environment variable
"""

import os
from langchain_xai import ChatXAI

MODEL_NAME = "grok-code-fast-1"


def main():
    # Check if API key is set
    if "XAI_API_KEY" not in os.environ:
        print("Please set XAI_API_KEY environment variable")
        print("You can get your API key from: https://console.x.ai/")
        return

    try:
        # Initialize ChatXAI with Grok model
        chat = ChatXAI(model=MODEL_NAME)

        # Simple input message
        message = "Hello ! I am Son"
        print(f"Sending message to Grok: {message}")
        print("=" * 50)

        # Get response from Grok
        response = chat.invoke(message)

        # Print the response
        print("Grok response:")
        print(response.content)

    except Exception as e:
        print(f"Error communicating with Grok: {e}")
        print("Make sure your XAI_API_KEY is valid and you have credits available")


if __name__ == "__main__":
    main()
