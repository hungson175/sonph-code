# MultiEdit Tool

## Description

This is a tool for making multiple edits to a single file in one operation. It is built on top of the Edit tool and allows you to perform multiple find-and-replace operations efficiently. Prefer this tool over the Edit tool when you need to make multiple edits to the same file.

## Prerequisites

1. Use the Read tool to understand the file's contents and context
2. Verify the directory path is correct

## Parameters

1. **file_path**: The absolute path to the file to modify (must be absolute, not relative)
2. **edits**: An array of edit operations to perform, where each edit contains:
   - **old_string**: The text to replace (must match the file contents exactly, including all whitespace and indentation)
   - **new_string**: The edited text to replace the old_string
   - **replace_all**: Replace all occurrences of old_string (optional, defaults to false)

## Important Constraints

- **Atomic Operations**: All edits are applied in sequence, in the order provided. Each edit operates on the result of the previous edit
- **All or Nothing**: All edits must be valid for the operation to succeed - if any edit fails, none will be applied
- **Sequential Processing**: Plan edits carefully to avoid conflicts between sequential operations
- For Jupyter notebooks (.ipynb files), use the NotebookEdit tool instead

## Critical Requirements

1. All edits follow the same requirements as the single Edit tool
2. The edits are atomic - either all succeed or none are applied
3. Plan your edits carefully to avoid conflicts between sequential operations

## Warnings

- The tool will fail if `edits.old_string` doesn't match the file contents exactly (including whitespace)
- The tool will fail if `edits.old_string` and `edits.new_string` are the same
- Since edits are applied in sequence, ensure that earlier edits don't affect the text that later edits are trying to find

## Best Practices

- Ensure all edits result in idiomatic, correct code
- Do not leave the code in a broken state
- Always use absolute file paths (starting with /)
- Only use emojis if the user explicitly requests it
- Use `replace_all` for renaming variables across the file

## Creating New Files

If you want to create a new file:
- Use a new file path, including dir name if needed
- First edit: empty old_string and the new file's contents as new_string
- Subsequent edits: normal edit operations on the created content

## Schema

```json
{
  "type": "object",
  "properties": {
    "file_path": {
      "type": "string",
      "description": "The absolute path to the file to modify"
    },
    "edits": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "old_string": {
            "type": "string",
            "description": "The text to replace"
          },
          "new_string": {
            "type": "string",
            "description": "The text to replace it with"
          },
          "replace_all": {
            "type": "boolean",
            "default": false,
            "description": "Replace all occurences of old_string (default false)."
          }
        },
        "required": [
          "old_string",
          "new_string"
        ],
        "additionalProperties": false
      },
      "minItems": 1,
      "description": "Array of edit operations to perform sequentially on the file"
    }
  },
  "required": [
    "file_path",
    "edits"
  ],
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
```