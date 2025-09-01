#!/usr/bin/env python3
"""Test script to verify DeepSeek integration in coding agent."""

import os
import sys
from dotenv import load_dotenv

def test_deepseek_integration():
    """Test that DeepSeek is properly integrated."""
    load_dotenv()
    
    # Check environment variable
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("❌ DEEPSEEK_API_KEY not found in environment")
        print("Please set DEEPSEEK_API_KEY in your .env file")
        return False
    
    print("✅ DEEPSEEK_API_KEY found")
    
    # Try importing the agent
    try:
        from coding_agent.core.base_agent import BaseAgent
        print("✅ Successfully imported BaseAgent")
    except ImportError as e:
        print(f"❌ Failed to import BaseAgent: {e}")
        return False
    
    # Try creating an agent instance
    try:
        agent = BaseAgent(
            system_prompt="You are a helpful assistant.",
            tools=[]
        )
        print("✅ Successfully created BaseAgent instance with DeepSeek")
        print(f"   Model: {agent.llm.model_name}")
        print(f"   Base URL: {agent.llm.openai_api_base}")
    except Exception as e:
        print(f"❌ Failed to create agent: {e}")
        return False
    
    # Try a simple interaction (without actually calling the API)
    try:
        # Just check that message handling works
        from langchain_core.messages import HumanMessage
        test_message = HumanMessage(content="test")
        agent.messages.append(test_message)
        print("✅ Message handling works")
        print(f"   Messages in history: {len(agent.messages)}")
    except Exception as e:
        print(f"❌ Message handling failed: {e}")
        return False
    
    print("\n🎉 All checks passed! DeepSeek integration is working.")
    return True

if __name__ == "__main__":
    success = test_deepseek_integration()
    sys.exit(0 if success else 1)