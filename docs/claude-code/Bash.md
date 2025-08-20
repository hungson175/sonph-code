# Bash Tool

## Description

Executes a given bash command in a persistent shell session with optional timeout, ensuring proper handling and security measures.

## Command Execution Guidelines

### Directory Verification
- If the command will create new directories or files, first use the LS tool to verify the parent directory exists and is the correct location
- For example, before running "mkdir foo/bar", first use LS to check that "foo" exists and is the intended parent directory

### Proper Quoting
Always quote file paths that contain spaces with double quotes:
- ✅ `cd "/Users/name/My Documents"` (correct)
- ❌ `cd /Users/name/My Documents` (incorrect - will fail)
- ✅ `python "/path/with spaces/script.py"` (correct)
- ❌ `python /path/with spaces/script.py` (incorrect - will fail)

## Usage Notes

- The command argument is required
- Optional timeout in milliseconds (up to 600000ms / 10 minutes). Default: 120000ms (2 minutes)
- Write a clear, concise description of what the command does in 5-10 words
- Output exceeding 30000 characters will be truncated
- Use `run_in_background` parameter to run commands in the background
- **IMPORTANT**: Avoid using search commands like `find` and `grep`. Use Grep, Glob, or Task tools instead
- **IMPORTANT**: Avoid read tools like `cat`, `head`, `tail`, and `ls`. Use Read and LS tools instead
- If you need `grep`, use ripgrep (`rg`) which is pre-installed
- Use `;` or `&&` to separate multiple commands. Do NOT use newlines
- Maintain current working directory by using absolute paths and avoiding `cd`

## Git Operations

### Committing Changes
When creating git commits:
1. Run git status, git diff, and git log commands in parallel
2. Analyze staged changes and draft commit message
3. Add untracked files and create commit with proper format
4. Verify commit succeeded with git status

### Pull Requests
1. Run git status, git diff, and git log commands to understand branch state
2. Analyze all changes for pull request summary
3. Push to remote if needed and create PR using `gh pr create`

## Schema

```json
{
  "type": "object",
  "properties": {
    "command": {
      "type": "string",
      "description": "The command to execute"
    },
    "timeout": {
      "type": "number",
      "description": "Optional timeout in milliseconds (max 600000)"
    },
    "description": {
      "type": "string",
      "description": " Clear, concise description of what this command does in 5-10 words"
    },
    "run_in_background": {
      "type": "boolean",
      "description": "Set to true to run this command in the background. Use BashOutput to read the output later."
    }
  },
  "required": [
    "command"
  ],
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
```