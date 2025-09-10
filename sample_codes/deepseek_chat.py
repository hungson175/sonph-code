#!/usr/bin/env python3
"""
DeepSeek Interactive Chat CLI

A simple command-line interface for chatting with DeepSeek models using LangChain.
Based on DeepSeek API documentation and LangChain integration.
"""

import os
import sys
from typing import List, Any
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


class DeepSeekChat:
    """Interactive chat interface for DeepSeek API using LangChain."""

    def __init__(self, api_key: str = None, model: str = "deepseek-chat"):
        """
        Initialize the DeepSeek chat client.

        Args:
            api_key: DeepSeek API key
            model: Model name (default: deepseek-chat)
        """
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.model = model or os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

        if not self.api_key:
            raise ValueError(
                "DeepSeek API key is required. Set DEEPSEEK_API_KEY environment variable or pass as parameter."
            )

        # Initialize LangChain ChatOpenAI with DeepSeek configuration
        self.client = ChatOpenAI(
            api_key=self.api_key, base_url="https://api.deepseek.com", model=self.model
        )

        # Conversation history using LangChain message types
        self.messages: List[Any] = [
            SystemMessage(content="You are a helpful AI assistant powered by DeepSeek.")
        ]

    def chat(self, user_input: str) -> str:
        """
        Send a message to DeepSeek and get response.

        Args:
            user_input: User's message

        Returns:
            Assistant's response
        """
        # Add user message to conversation history
        self.messages.append(HumanMessage(content=user_input))

        try:
            # Call DeepSeek API using LangChain
            response = self.client.invoke(self.messages)

            # Get assistant's response
            assistant_response = response.content

            # Add assistant's response to conversation history
            self.messages.append(AIMessage(content=assistant_response))

            return assistant_response

        except Exception as e:
            error_msg = f"Error communicating with DeepSeek API: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg

    def chat_stream(self, user_input: str):
        """
        Send a message to DeepSeek and stream the response.

        Args:
            user_input: User's message
        """
        # Add user message to conversation history
        self.messages.append(HumanMessage(content=user_input))

        try:
            # Call DeepSeek API with streaming using LangChain
            print("🤖 DeepSeek: ", end="", flush=True)
            full_response = ""

            for chunk in self.client.stream(self.messages):
                if chunk.content:
                    print(chunk.content, end="", flush=True)
                    full_response += chunk.content

            print()  # New line after streaming

            # Add assistant's response to conversation history
            self.messages.append(AIMessage(content=full_response))

        except Exception as e:
            error_msg = f"Error communicating with DeepSeek API: {str(e)}"
            print(f"❌ {error_msg}")

    def reset_conversation(self):
        """Reset the conversation history."""
        self.messages = [
            SystemMessage(content="You are a helpful AI assistant powered by DeepSeek.")
        ]
        print("🔄 Conversation history reset.")

    def show_help(self):
        """Show help information."""
        help_text = """
📋 Available Commands:
  /help    - Show this help message
  /reset   - Reset conversation history
  /exit    - Exit the chat
  /quit    - Exit the chat
  /model   - Show current model information
  /history - Show conversation history (first 3 and last 3 messages)
  
💬 Just type your message and press Enter to chat!
        """
        print(help_text)

    def show_model_info(self):
        """Show current model information."""
        print("🔧 Current Configuration:")
        print(f"   Model: {self.model}")
        print("   LangChain Integration: ChatOpenAI (DeepSeek API)")
        print(f"   Messages in history: {len(self.messages)}")

    def show_history(self):
        """Show conversation history (abbreviated)."""
        print("📝 Conversation History:")
        if len(self.messages) <= 6:
            for i, msg in enumerate(self.messages):
                role = type(msg).__name__.replace("Message", "").lower()
                content = (
                    msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
                )
                print(f"  {i+1}. {role}: {content}")
        else:
            # Show first 3 and last 3
            print("  (showing first 3 and last 3 messages):")
            for i in range(3):
                msg = self.messages[i]
                role = type(msg).__name__.replace("Message", "").lower()
                content = (
                    msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
                )
                print(f"  {i+1}. {role}: {content}")

            print("  ...")

            for i in range(len(self.messages) - 3, len(self.messages)):
                msg = self.messages[i]
                role = type(msg).__name__.replace("Message", "").lower()
                content = (
                    msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
                )
                print(f"  {i+1}. {role}: {content}")


def main():
    """Main function to run the interactive chat."""
    # Load environment variables
    load_dotenv()

    print("🚀 DeepSeek Interactive Chat CLI")
    print("=" * 50)

    try:
        # Initialize chat client
        chat = DeepSeekChat()
        print(f"✅ Connected to DeepSeek API (Model: {chat.model})")
        print("💡 Type '/help' for available commands")
        print("💬 Start chatting! Type '/exit' to quit.")
        print("-" * 50)

        while True:
            try:
                # Get user input
                user_input = input("👤 You: ").strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input.startswith("/"):
                    command = user_input.lower()

                    if command in ["/exit", "/quit"]:
                        print("👋 Goodbye!")
                        break
                    elif command == "/help":
                        chat.show_help()
                    elif command == "/reset":
                        chat.reset_conversation()
                    elif command == "/model":
                        chat.show_model_info()
                    elif command == "/history":
                        chat.show_history()
                    else:
                        print(f"❓ Unknown command: {user_input}")
                        print("💡 Type '/help' for available commands")
                    continue

                # Send message to DeepSeek (with streaming)
                chat.chat_stream(user_input)

            except KeyboardInterrupt:
                print("\n\n👋 Chat interrupted. Goodbye!")
                break
            except EOFError:
                print("\n\n👋 Goodbye!")
                break

    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("💡 Please set your DEEPSEEK_API_KEY environment variable")
        print("   You can copy 'env_example.txt' to '.env' and edit it")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
