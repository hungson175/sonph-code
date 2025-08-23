# Read Tool

## Description

Reads a file from the local filesystem. You can access any file directly by using this tool. Assume this tool is able to read all files on the machine. If the User provides a path to a file assume that path is valid. It is okay to read a file that does not exist; an error will be returned.

## Usage Guidelines

- **File path must be absolute**, not relative
- By default, reads up to 2000 lines starting from the beginning
- You can optionally specify line offset and limit for long files
- Lines longer than 2000 characters will be truncated
- Results returned using `cat -n` format, with line numbers starting at 1

## Supported File Types

- **Images** (PNG, JPG, etc.) - Contents presented visually as Claude Code is multimodal
- **PDF files** - Processed page by page, extracting text and visual content
- **Jupyter notebooks** (.ipynb) - Returns all cells with outputs, combining code, text, and visualizations
- **Screenshots** - Works with temporary file paths like `/var/folders/123/abc/T/TemporaryItems/NSIRD_screencaptureui_ZfB1tD/Screenshot.png`

## Performance Tips

- You have the capability to call multiple tools in a single response
- It's always better to speculatively read multiple files as a batch that are potentially useful
- If you read a file with empty contents, you'll receive a system reminder warning

## Schema

```json
{
  "type": "object",
  "properties": {
    "file_path": {
      "type": "string",
      "description": "The absolute path to the file to read"
    },
    "line_number": {
      "type": "number",
      "description": "The line number to start reading from. Only provide if the file is too large to read at once"
    },
    "reading_mode": {
      "type": "string",
      "description": "The mode to read the file: 'middle', 'top', 'bottom' - middle: read limit lines with line_number as the middle line, top: read limit lines with line_number as the first line, bottom: read limit lines with line_number as the last line"
    },
    "limit": {
      "type": "number",
      "description": "The number of lines to read. Only provide if the file is too large to read at once."
    }
  },
  "required": [
    "file_path"
  ],
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
```