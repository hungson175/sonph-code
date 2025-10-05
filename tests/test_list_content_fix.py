#!/usr/bin/env python3
"""Test that the agent handles list content properly"""

from coding_agent.core.agent import CodingAgent

# Create agent
agent = CodingAgent(provider_name="grok")

print("Testing list content handling - should not crash with 'list has no attribute strip'")
print("=" * 70)

# Test with the same prompt that was causing issues
response = agent.chat("Tạo game cờ caro (5 quân thẳng hàng/chéo, không phải tic-tac-toe) cho web sử dụng NextJS/ReactJS với thiết kế tối giản cho 2 người chơi, màu đen trắng - trông như kiểu cờ vây ấy. 3D đẹp đẹp tí, nhưng vẫn phải simple và elegant nhá !")

print("\n" + "=" * 70)
print("✅ Success! No 'list has no attribute strip' error")
print(f"Response type: {type(response)}")
print(f"Response preview: {str(response)[:200]}...")