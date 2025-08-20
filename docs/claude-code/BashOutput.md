# BashOutput Tool

## Description

- Retrieves output from a running or completed background bash shell
- Takes a shell_id parameter identifying the shell
- Always returns only new output since the last check
- Returns stdout and stderr output along with shell status
- Supports optional regex filtering to show only lines matching a pattern
- Use this tool when you need to monitor or check the output of a long-running shell
- Shell IDs can be found using the /bashes command

## Usage Scenarios

- Monitoring long-running background processes
- Checking progress of builds, tests, or deployments
- Retrieving output from previously started background shells
- Filtering output to show only relevant information

## Filtering

The optional `filter` parameter allows you to:
- Use regular expressions to filter output lines
- Only show lines matching a specific pattern
- Any lines that do not match will no longer be available to read

## Schema

```json
{
  "type": "object",
  "properties": {
    "bash_id": {
      "type": "string",
      "description": "The ID of the background shell to retrieve output from"
    },
    "filter": {
      "type": "string",
      "description": "Optional regular expression to filter the output lines. Only lines matching this regex will be included in the result. Any lines that do not match will no longer be available to read."
    }
  },
  "required": [
    "bash_id"
  ],
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
```