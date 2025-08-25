# Task Tool

## Description

Launch a new agent to handle complex, multi-step tasks autonomously. 

Available agent types and the tools they have access to:
- general-purpose: General-purpose agent for researching complex questions, searching for code, and executing multi-step tasks. When you are searching for a keyword or file and are not confident that you will find the right match in the first few tries use this agent to perform the search for you. (Tools: *)
- statusline-setup: Use this agent to configure the user's Claude Code status line setting. (Tools: Read, Edit)
- output-style-setup: Use this agent to create a Claude Code output style. (Tools: Read, Write, Edit, Glob, LS, Grep)
- octalysis-gamification-expert: Use this agent when you need to design or evaluate gamification strategies using the Octalysis Framework, create human-focused engagement systems, analyze user motivation patterns, or transform products/experiences to drive intrinsic motivation. Examples: <example>Context: User wants to improve user engagement in their learning app. user: 'Our learning app has low retention rates. Users complete the first few lessons but then drop off. How can we make it more engaging?' assistant: 'I'll use the octalysis-gamification-expert agent to analyze this retention problem and design a human-focused gamification strategy using the Octalysis Framework.' <commentary>The user needs gamification expertise to solve an engagement problem, which is exactly what this agent specializes in.</commentary></example> <example>Context: User is designing a fitness app and wants to avoid superficial gamification. user: 'I want to add gamification to my fitness app but I don't want it to feel cheap or gimmicky like just adding badges and points.' assistant: 'Let me engage the octalysis-gamification-expert agent to help you design meaningful, human-focused gamification that goes beyond surface-level mechanics.' <commentary>The user specifically wants to avoid shallow gamification, which aligns perfectly with this agent's expertise in human-focused design.</commentary></example> (Tools: *)
- ui-ux-designer: Use this agent when you need expert guidance on user interface design, user experience optimization, design systems, accessibility, usability testing, or visual design decisions. Examples: <example>Context: User is working on a financial dashboard and needs design guidance. user: 'I'm building a portfolio summary page for our wealth management app. What's the best way to display portfolio performance data?' assistant: 'Let me use the ui-ux-designer agent to provide expert design guidance for your portfolio dashboard.' <commentary>The user needs UI/UX expertise for designing a financial interface, so use the ui-ux-designer agent.</commentary></example> <example>Context: User wants feedback on their current design implementation. user: 'Can you review the user flow for our investment recommendation feature and suggest improvements?' assistant: 'I'll use the ui-ux-designer agent to analyze your user flow and provide UX recommendations.' <commentary>This requires UX expertise to evaluate user flows and suggest improvements.</commentary></example> (Tools: Task, Bash, Glob, Grep, LS, ExitPlanMode, Read, NotebookRead, WebFetch, TodoWrite, WebSearch, mcp__ide__getDiagnostics, mcp__ide__executeCode)
- faang-engineer-architect: Use this agent when you need expert-level software engineering and architecture guidance from someone with FAANG-level experience. This includes system design, code architecture decisions, performance optimization, scalability solutions, technical leadership advice, and solving complex engineering problems at scale. Examples:
- <example>
  Context: User needs help designing a distributed system
  user: "I need to design a real-time notification system that can handle millions of users"
  assistant: "I'll use the Task tool to launch the faang-engineer-architect agent to help design this scalable system"
  <commentary>
  Since this requires expertise in large-scale system design typical of FAANG companies, use the faang-engineer-architect agent.
  </commentary>
</example>
- <example>
  Context: User wants architectural review of their codebase
  user: "Can you review my microservices architecture and suggest improvements?"
  assistant: "Let me use the faang-engineer-architect agent to provide an expert architectural review"
  <commentary>
  Architectural reviews benefit from FAANG-level engineering experience, so use this specialized agent.
  </commentary>
</example> (Tools: *)
- product-manager-faang-startup: Use this agent when you need strategic product guidance, feature prioritization, go-to-market strategies, user research insights, growth hacking tactics, or product roadmap development. This agent excels at balancing user needs with business objectives, defining MVPs, creating product specs, analyzing metrics, and making data-driven product decisions. Perfect for product strategy discussions, feature scoping, user story creation, A/B testing strategies, and product-market fit analysis. (Tools: *)
- cpo-strategic-advisor: Use this agent when you need strategic product leadership insights, product vision development, roadmap prioritization, stakeholder alignment strategies, or executive-level product decisions. This agent provides CPO-level perspective on product strategy, team scaling, market positioning, and balancing innovation with execution. Examples:

<example>
Context: User needs help with product strategy decisions
user: "How should I prioritize features for our Q2 roadmap given limited engineering resources?"
assistant: "I'll use the Task tool to launch the cpo-strategic-advisor agent to provide executive-level guidance on roadmap prioritization."
<commentary>
Since the user needs strategic product prioritization advice, use the cpo-strategic-advisor agent for CPO-level insights.
</commentary>
</example>

<example>
Context: User is facing product-market fit challenges
user: "We're struggling to find product-market fit in our B2B SaaS. What metrics should we focus on?"
assistant: "Let me engage the cpo-strategic-advisor agent to provide strategic guidance on achieving product-market fit."
<commentary>
The user needs high-level product strategy advice, which is perfect for the cpo-strategic-advisor agent.
</commentary>
</example>

<example>
Context: User needs help with product team structure
user: "We're scaling from 10 to 50 engineers. How should I structure my product organization?"
assistant: "I'll use the cpo-strategic-advisor agent to provide guidance on scaling product organizations effectively."
<commentary>
Organizational scaling questions require CPO-level experience, making this ideal for the cpo-strategic-advisor agent.
</commentary>
</example> (Tools: *)

When using the Task tool, you must specify a subagent_type parameter to select which agent type to use.



When NOT to use the Agent tool:
- If you want to read a specific file path, use the Read or Glob tool instead of the Agent tool, to find the match more quickly
- If you are searching for a specific class definition like "class Foo", use the Glob tool instead, to find the match more quickly
- If you are searching for code within a specific file or set of 2-3 files, use the Read tool instead of the Agent tool, to find the match more quickly
- Other tasks that are not related to the agent descriptions above


Usage notes:
1. Launch multiple agents concurrently whenever possible, to maximize performance; to do that, use a single message with multiple tool uses
2. When the agent is done, it will return a single message back to you. The result returned by the agent is not visible to the user. To show the user the result, you should send a text message back to the user with a concise summary of the result.
3. Each agent invocation is stateless. You will not be able to send additional messages to the agent, nor will the agent be able to communicate with you outside of its final report. Therefore, your prompt should contain a highly detailed task description for the agent to perform autonomously and you should specify exactly what information the agent should return back to you in its final and only message to you.
4. The agent's outputs should generally be trusted
5. Clearly tell the agent whether you expect it to write code or just to do research (search, file reads, web fetches, etc.), since it is not aware of the user's intent
6. If the agent description mentions that it should be used proactively, then you should try your best to use it without the user having to ask for it first. Use your judgement.

Example usage:

<example_agent_descriptions>
"code-reviewer": use this agent after you are done writing a signficant piece of code
"greeting-responder": use this agent when to respond to user greetings with a friendly joke
</example_agent_description>

<example>
user: "Please write a function that checks if a number is prime"
assistant: Sure let me write a function that checks if a number is prime
assistant: First let me use the Write tool to write a function that checks if a number is prime
assistant: I'm going to use the Write tool to write the following code:
<code>
function isPrime(n) {
  if (n <= 1) return false
  for (let i = 2; i * i <= n; i++) {
    if (n % i === 0) return false
  }
  return true
}
</code>
<commentary>
Since a signficant piece of code was written and the task was completed, now use the code-reviewer agent to review the code
</commentary>
assistant: Now let me use the code-reviewer agent to review the code
assistant: Uses the Task tool to launch the with the code-reviewer agent 
</example>

<example>
user: "Hello"
<commentary>
Since the user is greeting, use the greeting-responder agent to respond with a friendly joke
</commentary>
assistant: "I'm going to use the Task tool to launch the with the greeting-responder agent"
</example>


## Schema

```json
{
  "type": "object",
  "properties": {
    "description": {
      "type": "string",
      "description": "A short (3-5 word) description of the task"
    },
    "prompt": {
      "type": "string",
      "description": "The task for the agent to perform"
    },
    "subagent_type": {
      "type": "string",
      "description": "The type of specialized agent to use for this task"
    }
  },
  "required": [
    "description",
    "prompt",
    "subagent_type"
  ],
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
```

## Implementation Notes

This tool has been updated to match the exact parameter descriptions from the original Claude Code JSON schema:

- **description**: "A short (3-5 word) description of the task"
- **prompt**: "The task for the agent to perform"
- **subagent_type**: "The type of specialized agent to use for this task"

### Current Implementation

Currently only supports the `general-purpose` subagent type, which provides access to all available tools (*) for:
- Researching complex questions
- Searching for code
- Executing multi-step tasks
- File system operations

### Usage Guidelines

The comprehensive description includes detailed usage notes, examples, and behavioral guidance for when to use/not use the Task tool, ensuring optimal delegation of work to specialized agents.
