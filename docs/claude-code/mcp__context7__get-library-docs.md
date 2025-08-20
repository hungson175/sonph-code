# mcp__context7__get-library-docs Tool

## Description

Fetches up-to-date documentation for a library. You must call 'resolve-library-id' first to obtain the exact Context7-compatible library ID required to use this tool, **UNLESS** the user explicitly provides a library ID in the format '/org/project' or '/org/project/version' in their query.

## Prerequisites

- Call `mcp__context7__resolve-library-id` first to get the correct library ID
- OR user provides explicit library ID in format `/org/project` or `/org/project/version`

## Library ID Format

Context7-compatible library IDs follow these patterns:
- `/org/project` (e.g., `/mongodb/docs`, `/vercel/next.js`, `/supabase/supabase`)
- `/org/project/version` (e.g., `/vercel/next.js/v14.3.0-canary.87`)

## Parameters

- **context7CompatibleLibraryID** (required): Exact library ID from resolve-library-id or user query
- **topic** (optional): Focus documentation on specific topic (e.g., 'hooks', 'routing')
- **tokens** (optional): Maximum tokens to retrieve (default: 10000). Higher values provide more context but consume more tokens

## Use Cases

- Getting up-to-date library documentation
- Focusing on specific topics within a library
- Retrieving code examples and usage patterns
- Understanding API changes and new features

## Schema

```json
{
  "type": "object",
  "properties": {
    "context7CompatibleLibraryID": {
      "type": "string",
      "description": "Exact Context7-compatible library ID (e.g., '/mongodb/docs', '/vercel/next.js', '/supabase/supabase', '/vercel/next.js/v14.3.0-canary.87') retrieved from 'resolve-library-id' or directly from user query in the format '/org/project' or '/org/project/version'."
    },
    "topic": {
      "type": "string",
      "description": "Topic to focus documentation on (e.g., 'hooks', 'routing')."
    },
    "tokens": {
      "type": "number",
      "description": "Maximum number of tokens of documentation to retrieve (default: 10000). Higher values provide more context but consume more tokens."
    }
  },
  "required": [
    "context7CompatibleLibraryID"
  ],
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
```