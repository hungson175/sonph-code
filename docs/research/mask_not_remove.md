# Mask, Don't Remove: Tool Management for AI Agents

*Understanding the "Mask, Don't Remove" principle from Manus AI's context engineering approach*

## The Core Problem

When building AI agents with many tools, you face a fundamental dilemma:

- **Too many tools**: Agent makes poor choices, selects wrong tools, takes inefficient paths
- **Dynamic tool removal**: Breaks KV-cache, confuses model when previous actions reference missing tools

The naive solution is to dynamically add/remove tools from the context based on current needs. This creates two critical problems:

1. **Cache invalidation**: Tool definitions typically appear early in the prompt. Any change invalidates the KV-cache for all subsequent content.
2. **Context confusion**: When previous actions reference tools that are no longer defined, the model gets confused and may hallucinate or produce schema violations.

## The Solution: Logit Masking

Instead of changing which tools are available, you control which tools the model can select during the decoding process.

### Key Concept: Separating Definition from Selection

- **Tools remain defined** in the context (preserves cache)
- **Selection is constrained** during decoding (maintains coherence)

## Understanding Logits in Application Context

For LLM application developers, here's what you need to know about logits:

### What Are Logits?

Logits are the raw numerical scores the model outputs before they become probabilities.

**Normal process:**
1. Model outputs raw scores: `browser_click: 2.1, shell_run: 1.3, file_write: 0.8`
2. Softmax converts to probabilities: `70%, 20%, 10%`  
3. System samples based on probabilities

**With masking:**
1. Model outputs raw scores: `browser_click: 2.1, shell_run: 1.3, file_write: 0.8`
2. **You intercept and modify**: `browser_click: 2.1, shell_run: -∞, file_write: -∞`
3. Softmax converts: `99.9%, 0.05%, 0.05%`
4. System effectively can only choose browser tools

### Practical Implementation

#### Method 1: API-Level Constraints

Many LLM APIs provide built-in ways to constrain generation:

**OpenAI API:**
```python
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=messages,
    functions=all_tools,  # All tools defined
    logit_bias={
        "shell_": -100,    # Suppress shell tools
        "file_": -100      # Suppress file tools
    }
)
```

**Claude API (via prefilling):**
```python
response = anthropic.messages.create(
    model="claude-3-sonnet",
    messages=messages + [{
        "role": "assistant", 
        "content": "<tool_call>\n{\"name\": \"browser_"  # Force browser tools
    }]
)
```

#### Method 2: Local Inference with Custom Processors

For self-hosted models using libraries like `transformers`:

```python
from transformers import LogitsProcessor

class ToolMaskProcessor(LogitsProcessor):
    def __init__(self, tokenizer, allowed_prefixes):
        self.tokenizer = tokenizer
        self.allowed_prefixes = allowed_prefixes
    
    def __call__(self, input_ids, scores):
        # Get all possible tokens
        vocab = self.tokenizer.get_vocab()
        
        for token, token_id in vocab.items():
            # Check if token starts with allowed prefix
            if not any(token.startswith(prefix) for prefix in self.allowed_prefixes):
                scores[0, token_id] = float('-inf')  # Mask unwanted tokens
        
        return scores

# Usage
processor = ToolMaskProcessor(tokenizer, ["browser_"])
output = model.generate(
    input_ids, 
    logits_processor=[processor],
    do_sample=True
)
```

#### Method 3: Response Prefilling

This is the most elegant approach mentioned in the Manus article:

**Three constraint modes:**

1. **Auto** - Model chooses whether to call any function:
   ```
   Prefill: "<|im_start|>assistant"
   ```

2. **Required** - Model must call some function:
   ```
   Prefill: "<|im_start|>assistant\n<tool_call>"
   ```

3. **Specified** - Model must call function from specific category:
   ```
   Prefill: "<|im_start|>assistant\n<tool_call>\n{\"name\": \"browser_"
   ```

### Smart Tool Naming Strategy

To make masking effective, use consistent prefixes:

```python
# Good: Categorical prefixes
tools = [
    "browser_click", "browser_scroll", "browser_navigate",
    "shell_run", "shell_cd", "shell_ls", 
    "file_read", "file_write", "file_delete"
]

# Usage: Easily constrain to browser tools only
allowed_prefixes = ["browser_"]
```

## State Machine Integration

The Manus approach combines logit masking with a state machine:

```python
class AgentStateMachine:
    def get_allowed_tool_prefixes(self, current_state, context):
        if current_state == "user_input_received":
            return []  # Must respond, not call tools
        elif current_state == "web_research":
            return ["browser_"]  # Only browser tools
        elif current_state == "file_analysis": 
            return ["file_"]  # Only file tools
        else:
            return ["browser_", "shell_", "file_"]  # All tools
```

## Benefits of This Approach

1. **Cache Efficiency**: All tools remain in context, maximizing KV-cache hits
2. **Context Coherence**: Previous tool calls remain valid references
3. **Flexible Control**: Fine-grained control over tool selection without prompt modification
4. **Performance**: No need to regenerate tool definitions or modify context

## Framework Support

| Framework/API | Logit Masking | Prefilling | Notes |
|---------------|---------------|------------|-------|
| OpenAI API | ✅ `logit_bias` | ❌ | Token-level bias |
| Anthropic API | ❌ | ✅ | Via message prefilling |
| vLLM | ✅ | ✅ | Custom processors + prefill |
| TensorRT-LLM | ✅ | ✅ | Built-in constraints |
| Transformers | ✅ | ✅ | LogitsProcessor classes |

## Implementation Considerations

### Token Boundary Issues
When masking, be aware of tokenization:
- `"browser_click"` might be split into `["browser", "_", "click"]`
- Need to mask the right token pieces

### Performance Impact
- Logit masking adds minimal overhead
- Much faster than context modification
- Prefilling is nearly free

### Debugging
```python
# Log what tokens are being masked
def debug_mask(scores, tokenizer):
    masked_tokens = []
    for i, score in enumerate(scores[0]):
        if score == float('-inf'):
            token = tokenizer.decode([i])
            masked_tokens.append(token)
    print(f"Masked tokens: {masked_tokens}")
```

## Conclusion

The "Mask, Don't Remove" principle elegantly solves the tool management problem in AI agents by separating tool definition from tool selection. By leveraging the decoding process rather than modifying the prompt, you can maintain cache efficiency while providing fine-grained control over agent behavior.

This approach is particularly valuable for production AI agents where both performance and reliability are critical. The technique works across different model providers and can be implemented at various levels of the inference stack.

The key insight: **hack the decoding process, not the prompt**.