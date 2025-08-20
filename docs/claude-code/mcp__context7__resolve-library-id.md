# mcp__context7__resolve-library-id Tool

## Description

Resolves a package/product name to a Context7-compatible library ID and returns a list of matching libraries.

## Usage Requirements

You **MUST** call this function before 'get-library-docs' to obtain a valid Context7-compatible library ID **UNLESS** the user explicitly provides a library ID in the format '/org/project' or '/org/project/version' in their query.

## Selection Process

1. **Analyze the query** to understand what library/package the user is looking for
2. **Return the most relevant match** based on:
   - Name similarity to the query (exact matches prioritized)
   - Description relevance to the query's intent
   - Documentation coverage (prioritize libraries with higher Code Snippet counts)
   - Trust score (consider libraries with scores of 7-10 more authoritative)

## Response Format

- Return the selected library ID in a clearly marked section
- Provide a brief explanation for why this library was chosen
- If multiple good matches exist, acknowledge this but proceed with the most relevant one
- If no good matches exist, clearly state this and suggest query refinements

## Handling Ambiguity

For ambiguous queries, request clarification before proceeding with a best-guess match.

## Schema

```json
{
  "type": "object",
  "properties": {
    "libraryName": {
      "type": "string",
      "description": "Library name to search for and retrieve a Context7-compatible library ID."
    }
  },
  "required": [
    "libraryName"
  ],
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
```