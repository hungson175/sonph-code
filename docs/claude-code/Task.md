# Task Tool

## Description

Launch a new agent to handle complex, multi-step tasks autonomously. 

## Available Agent Types

### general-purpose
General-purpose agent for researching complex questions, searching for code, and executing multi-step tasks. When you are searching for a keyword or file and are not confident that you will find the right match in the first few tries use this agent to perform the search for you. (Tools: *)

### statusline-setup
Use this agent to configure the user's Claude Code status line setting. (Tools: Read, Edit)

### output-style-setup
Use this agent to create a Claude Code output style. (Tools: Read, Write, Edit, Glob, LS, Grep)

### octalysis-gamification-expert
Use this agent when you need to design or evaluate gamification strategies using the Octalysis Framework, create human-focused engagement systems, analyze user motivation patterns, or transform products/experiences to drive intrinsic motivation. (Tools: *)

### ui-ux-designer
Use this agent when you need expert guidance on user interface design, user experience optimization, design systems, accessibility, usability testing, or visual design decisions. (Tools: Task, Bash, Glob, Grep, LS, ExitPlanMode, Read, NotebookRead, WebFetch, TodoWrite, WebSearch, mcp__ide__getDiagnostics, mcp__ide__executeCode)

### faang-engineer-architect
Use this agent when you need expert-level software engineering and architecture guidance from someone with FAANG-level experience. This includes system design, code architecture decisions, performance optimization, scalability solutions, technical leadership advice, and solving complex engineering problems at scale. (Tools: *)

### product-manager-faang-startup
Use this agent when you need strategic product guidance, feature prioritization, go-to-market strategies, user research insights, growth hacking tactics, or product roadmap development. This agent excels at balancing user needs with business objectives, defining MVPs, creating product specs, analyzing metrics, and making data-driven product decisions. Perfect for product strategy discussions, feature scoping, user story creation, A/B testing strategies, and product-market fit analysis. (Tools: *)

### cpo-strategic-advisor
Use this agent when you need strategic product leadership insights, product vision development, roadmap prioritization, stakeholder alignment strategies, or executive-level product decisions. This agent provides CPO-level perspective on product strategy, team scaling, market positioning, and balancing innovation with execution. (Tools: *)

## Usage Notes

1. Launch multiple agents concurrently whenever possible, to maximize performance; to do that, use a single message with multiple tool uses
2. When the agent is done, it will return a single message back to you. The result returned by the agent is not visible to the user. To show the user the result, you should send a text message back to the user with a concise summary of the result.
3. Each agent invocation is stateless. You will not be able to send additional messages to the agent, nor will the agent be able to communicate with you outside of its final report. Therefore, your prompt should contain a highly detailed task description for the agent to perform autonomously and you should specify exactly what information the agent should return back to you in its final and only message to you.
4. The agent's outputs should generally be trusted
5. Clearly tell the agent whether you expect it to write code or just to do research (search, file reads, web fetches, etc.), since it is not aware of the user's intent
6. If the agent description mentions that it should be used proactively, then you should try your best to use it without the user having to ask for it first. Use your judgement.

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