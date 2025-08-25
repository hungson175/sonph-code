"""File manipulation tools."""

import os
from langchain_core.tools import tool

from ..core.config import Config


@tool("Read")
def read_file(
    file_path: str,
    line_number: int = None,
    limit: int = None,
    read_mode: str = "top_down",
) -> str:
    """Reads a file from the local filesystem. You can access any file directly by using this tool. Assume this tool is able to read all files on the machine. If the User provides a path to a file assume that path is valid. It is okay to read a file that does not exist; an error will be returned.

    ## Usage Guidelines

    - **File path must be absolute**, not relative
    - By default, reads up to {Config.DEFAULT_READ_LIMIT} lines starting from the beginning
    - You can optionally specify line_number, limit, and read_mode for better context
    - Lines longer than {Config.DEFAULT_READ_LIMIT} characters will be truncated
    - Results returned using `cat -n` format, with line numbers starting at 1

    ## Read Modes

    - **"top_down"** (default): Read N lines starting from line_number
    - **"middle"**: Read N lines centered around line_number
    - **"bottom_up"**: Read N lines ending at line_number

    ## Supported File Types

    - **Images** (PNG, JPG, etc.) - Contents presented visually as Claude Code is multimodal
    - **PDF files** - Processed page by page, extracting text and visual content
    - **Jupyter notebooks** (.ipynb) - Returns all cells with outputs, combining code, text, and visualizations
    - **Screenshots** - Works with temporary file paths like `/var/folders/123/abc/T/TemporaryItems/NSIRD_screencaptureui_ZfB1tD/Screenshot.png`

    ## Performance Tips

    - You have the capability to call multiple tools in a single response
    - It's always better to speculatively read multiple files as a batch that are potentially useful
    - If you read a file with empty contents, you'll receive a system reminder warning

        Args:
            file_path: The absolute path to the file to read
            line_number: The target line number for reading context
            limit: The number of lines to read
            read_mode: How to read around line_number ("top_down", "middle", "bottom_up")
        Returns:
            File contents in cat -n format with line numbers, or error message
    """
    try:
        with open(file_path, "r") as f:
            lines = f.readlines()

        # Calculate reading range based on read_mode
        total_lines = len(lines)
        read_limit = limit if limit else Config.DEFAULT_READ_LIMIT

        if line_number is None:
            # Default behavior: read from beginning
            start = 0
            end = min(read_limit, total_lines)
        else:
            line_idx = line_number - 1  # Convert to 0-based index

            if read_mode == "middle":
                # Center around line_number
                half_limit = read_limit // 2
                start = max(0, line_idx - half_limit)
                end = min(total_lines, start + read_limit)
            elif read_mode == "bottom_up":
                # Read N lines ending at line_number
                end = min(total_lines, line_idx + 1)
                start = max(0, end - read_limit)
            else:  # "top_down" (default)
                # Read N lines starting from line_number
                start = max(0, line_idx)
                end = min(total_lines, start + read_limit)

        # Format with line numbers like cat -n
        result = []
        for i in range(start, min(end, len(lines))):
            line_num = i + 1
            line = (
                lines[i][: Config.DEFAULT_READ_LIMIT]
                if len(lines[i]) > Config.DEFAULT_READ_LIMIT
                else lines[i]
            )
            result.append(f"{line_num:6d}\t{line.rstrip()}")

        return "\n".join(result)
    except FileNotFoundError:
        return f"File not found: {file_path}"
    except Exception as e:
        return f"Error reading file: {str(e)}"


@tool("Write")
def write_file(file_path: str, content: str) -> str:
    """Writes a file to the local filesystem.

    ## Usage Guidelines

    - This tool will **overwrite the existing file** if there is one at the provided path
    - If this is an existing file, you **MUST use the Read tool first** to read the file's contents. This tool will fail if you did not read the file first
    - **ALWAYS prefer editing existing files** in the codebase. NEVER write new files unless explicitly required
    - **NEVER proactively create documentation files** (*.md) or README files. Only create documentation files if explicitly requested by the User
    - Only use emojis if the user explicitly requests it. Avoid writing emojis to files unless asked

    ## Best Practices

    - Use absolute file paths (must be absolute, not relative)
    - Read existing files before overwriting them
    - Prefer Edit or MultiEdit tools for modifying existing content
    - Only create new files when specifically required for the task

        Args:
            file_path: The absolute path to the file to write (must be absolute, not relative)
            content: The content to write to the file
        Returns:
            Success message or error
    """
    try:
        # Create directory if it doesn't exist
        dir_path = os.path.dirname(file_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

        with open(file_path, "w") as f:
            f.write(content)
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"


@tool("Edit")
def edit_file(
    file_path: str, old_string: str, new_string: str, replace_all: bool = False
) -> str:
    """Performs exact string replacements in files.

    ## Usage Requirements

    - **Must use Read tool first** - This tool will error if you attempt an edit without reading the file
    - When editing text from Read tool output, preserve exact indentation (tabs/spaces) as it appears AFTER the line number prefix
    - Line number prefix format: `spaces + line number + tab`. Everything after that tab is the actual file content to match
    - **Never include any part of the line number prefix** in the old_string or new_string

    ## Best Practices

    - **ALWAYS prefer editing existing files** in the codebase. NEVER write new files unless explicitly required
    - Only use emojis if the user explicitly requests it. Avoid adding emojis to files unless asked
    - The edit will FAIL if `old_string` is not unique in the file. Either provide a larger string with more surrounding context to make it unique or use `replace_all` to change every instance
    - Use `replace_all` for replacing and renaming strings across the file. This parameter is useful for renaming variables

        Args:
            file_path: The absolute path to the file to modify
            old_string: The text to replace
            new_string: The text to replace it with (must be different from old_string)
            replace_all: Replace all occurences of old_string (default false)
        Returns:
            Success message or error
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            return f"Error: File not found: {file_path}"

        # Check if old_string and new_string are the same
        if old_string == new_string:
            return "Error: old_string and new_string cannot be the same"

        # Read the file
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check if old_string exists in the file
        if old_string not in content:
            return f"Error: String not found in file: {repr(old_string)}"

        # Check for uniqueness if not replace_all
        if not replace_all and content.count(old_string) > 1:
            return f"Error: String appears {content.count(old_string)} times in file. Use replace_all=True or provide more context to make it unique"

        # Perform the replacement
        if replace_all:
            new_content = content.replace(old_string, new_string)
            count = content.count(old_string)
        else:
            new_content = content.replace(old_string, new_string, 1)
            count = 1

        # Write the modified content back
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        action = (
            f"Replaced {count} occurrence(s)"
            if replace_all or count > 1
            else "Replaced"
        )
        return f"{action} in {file_path}"

    except Exception as e:
        return f"Error editing file: {str(e)}"


@tool("LS")
def list_files(path: str, ignore: list = None) -> str:
    """Lists files and directories in a given path. The path parameter must be an absolute path, not a relative path. You can optionally provide an array of glob patterns to ignore with the ignore parameter. You should generally prefer the Glob and Grep tools, if you know which directories to search.

    ## Usage Notes

    - **Path must be absolute**, not relative
    - Optional `ignore` parameter with array of glob patterns to exclude
    - Generally prefer Glob and Grep tools when you know which directories to search
    - Useful for exploring directory structure and verifying paths exist

        Args:
            path: The absolute path to the directory to list (must be absolute, not relative)
            ignore: List of glob patterns to ignore
        Returns:
            List of files and directories, or error message
    """
    try:
        import fnmatch

        if not os.path.isabs(path):
            return f"Error: Path must be absolute, got relative path: {path}"

        if not os.path.exists(path):
            return f"Directory not found: {path}"

        if not os.path.isdir(path):
            return f"Not a directory: {path}"

        items = []
        for item in sorted(os.listdir(path)):
            # Check if should ignore
            if ignore:
                skip = False
                for pattern in ignore:
                    if fnmatch.fnmatch(item, pattern):
                        skip = True
                        break
                if skip:
                    continue

            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                items.append(f"{item}/")
            else:
                items.append(item)

        if not items:
            return f"Empty directory: {path}"

        return "\n".join(items)
    except Exception as e:
        return f"Error listing directory: {str(e)}"
