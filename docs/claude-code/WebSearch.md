# WebSearch Tool

## Description

- Allows Claude to search the web and use the results to inform responses
- Provides up-to-date information for current events and recent data
- Returns search result information formatted as search result blocks
- Use this tool for accessing information beyond Claude's knowledge cutoff
- Searches are performed automatically within a single API call

## Usage Notes

- Domain filtering is supported to include or block specific websites
- Web search is only available in the US
- Account for "Today's date" in environment variables. For example, if environment says "Today's date: 2025-07-01", and the user wants the latest docs, do not use 2024 in the search query. Use 2025.

## Use Cases

- Finding current information beyond knowledge cutoff
- Researching recent developments or changes
- Gathering data from specific domains
- Excluding unreliable sources from search results

## Domain Filtering

- **allowed_domains**: Only include search results from these domains
- **blocked_domains**: Never include search results from these domains

## Schema

```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "minLength": 2,
      "description": "The search query to use"
    },
    "allowed_domains": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "Only include search results from these domains"
    },
    "blocked_domains": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "Never include search results from these domains"
    }
  },
  "required": [
    "query"
  ],
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
```