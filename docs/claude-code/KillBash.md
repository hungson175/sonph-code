# KillBash Tool

## Description

- Kills a running background bash shell by its ID
- Takes a shell_id parameter identifying the shell to kill
- Returns a success or failure status 
- Use this tool when you need to terminate a long-running shell
- Shell IDs can be found using the /bashes command

## Usage Scenarios

- Terminating runaway or stuck background processes
- Cleaning up after completed tasks
- Stopping long-running builds or tests when no longer needed
- Managing resource usage by stopping unnecessary background shells

## Finding Shell IDs

Use the `/bashes` command to list all running background shells and their IDs.

## Schema

```json
{
  "type": "object",
  "properties": {
    "shell_id": {
      "type": "string",
      "description": "The ID of the background shell to kill"
    }
  },
  "required": [
    "shell_id"
  ],
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
```