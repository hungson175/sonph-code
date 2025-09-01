"""Search and discovery tools."""

import glob
import os
import subprocess
from langchain_core.tools import tool


@tool("Glob")
def glob_files(pattern: str, path: str = None) -> str:
    """Fast file pattern matching tool that works with any codebase size.

    ## Features

    - Supports glob patterns like `**/*.js` or `src/**/*.ts`
    - Returns matching file paths sorted by modification time
    - Use this tool when you need to find files by name patterns
    - When doing an open ended search that may require multiple rounds of globbing and grepping, use the Task tool instead
    - You have the capability to call multiple tools in a single response. It is always better to speculatively perform multiple searches as a batch that are potentially useful

    ## Usage Examples

    - `**/*.js` - Find all JavaScript files recursively
    - `src/**/*.ts` - Find all TypeScript files in src directory
    - `*.md` - Find all Markdown files in current directory
    - `test/**/*.spec.js` - Find all spec files in test directory

        Args:
            pattern: The glob pattern to match files against
            path: The directory to search in. If not specified, the current working directory will be used. IMPORTANT: Omit this field to use the default directory. DO NOT enter "undefined" or "null" - simply omit it for the default behavior. Must be a valid directory path if provided.
        Returns:
            Matching file paths sorted by modification time, or error message
    """
    try:
        # Use current directory if path not specified
        search_path = path if path else "."

        # Handle absolute path in pattern
        if os.path.isabs(pattern):
            full_pattern = pattern
        else:
            full_pattern = os.path.join(search_path, pattern)

        # Get matching files using glob
        matches = glob.glob(full_pattern, recursive=True)

        if not matches:
            return f"No files found matching pattern: {pattern}"

        # Sort by modification time (newest first)
        matches.sort(key=lambda x: os.path.getmtime(x), reverse=True)

        # Return only files, not directories
        files = [f for f in matches if os.path.isfile(f)]

        if not files:
            return f"No files found matching pattern: {pattern}"

        return "\n".join(files)
    except Exception as e:
        return f"Error in glob search: {str(e)}"


@tool("Grep")
def grep_files(
    pattern: str,
    path: str = None,
    glob: str = None,
    output_mode: str = "files_with_matches",
    type: str = None,
    head_limit: int = None,
    multiline: bool = False,
    A: int = None,
    B: int = None,
    C: int = None,
    n: bool = False,
    i: bool = False,
) -> str:
    """A powerful search tool built on ripgrep.

    ## Usage Guidelines

    - **ALWAYS** use Grep for search tasks. NEVER invoke `grep` or `rg` as a Bash command. The Grep tool has been optimized for correct permissions and access.
    - Supports full regex syntax (e.g., `log.*Error`, `function\\\\s+\\\\w+`)
    - Filter files with glob parameter (e.g., `*.js`, `**/*.tsx`) or type parameter (e.g., `js`, `py`, `rust`)
    - Use Task tool for open-ended searches requiring multiple rounds
    - Pattern syntax: Uses ripgrep (not grep) - literal braces need escaping (use `interface\\\\{\\\\}` to find `interface{}` in Go code)
    - Multiline matching: By default patterns match within single lines only. For cross-line patterns, use `multiline: true`

    ## Output Modes

    - **`content`** - Shows matching lines (supports -A/-B/-C context, -n line numbers, head_limit)
    - **`files_with_matches`** - Shows only file paths (default, supports head_limit)
    - **`count`** - Shows match counts (supports head_limit)

    ## Context Options

    - `-A` - Number of lines to show after each match
    - `-B` - Number of lines to show before each match
    - `-C` - Number of lines to show before and after each match
    - `-n` - Show line numbers in output
    - `-i` - Case insensitive search

        Args:
            pattern: The regular expression pattern to search for in file contents
            path: File or directory to search in (rg PATH). Defaults to current working directory.
            glob: Glob pattern to filter files (e.g. "*.js", "*.{ts,tsx}") - maps to rg --glob
            output_mode: Output mode: "content" shows matching lines (supports -A/-B/-C context, -n line numbers, head_limit), "files_with_matches" shows file paths (supports head_limit), "count" shows match counts (supports head_limit). Defaults to "files_with_matches".
            type: File type to search (rg --type). Common types: js, py, rust, go, java, etc. More efficient than include for standard file types.
            head_limit: Limit output to first N lines/entries, equivalent to "| head -N". Works across all output modes: content (limits output lines), files_with_matches (limits file paths), count (limits count entries). When unspecified, shows all results from ripgrep.
            multiline: Enable multiline mode where . matches newlines and patterns can span lines (rg -U --multiline-dotall). Default: false.
            A: Number of lines to show after each match (rg -A). Requires output_mode: "content", ignored otherwise.
            B: Number of lines to show before each match (rg -B). Requires output_mode: "content", ignored otherwise.
            C: Number of lines to show before and after each match (rg -C). Requires output_mode: "content", ignored otherwise.
            n: Show line numbers in output (rg -n). Requires output_mode: "content", ignored otherwise.
            i: Case insensitive search (rg -i)
        Returns:
            Search results based on output_mode, or error message
    """
    try:
        # Try to find ripgrep using standard methods
        import shutil

        rg_cmd = shutil.which("rg")

        if not rg_cmd:
            # Try common installation locations
            rg_paths = [
                "/usr/local/bin/rg",
                "/opt/homebrew/bin/rg",
                "/usr/bin/rg",
                os.path.expanduser("~/.local/bin/rg"),
                os.path.expanduser("~/.cargo/bin/rg"),
            ]

            for rg_path in rg_paths:
                if os.path.isfile(rg_path) and os.access(rg_path, os.X_OK):
                    rg_cmd = rg_path
                    break

        if not rg_cmd:
            return "Error: ripgrep (rg) not found. Please install ripgrep or ensure it's in PATH."

        cmd = [rg_cmd]

        # Add pattern
        cmd.append(pattern)

        # Add path if specified
        if path:
            cmd.append(path)

        # Add flags based on parameters
        if i:
            cmd.append("-i")
        if multiline:
            cmd.extend(["-U", "--multiline-dotall"])
        if n and output_mode == "content":
            cmd.append("-n")
        if A is not None and output_mode == "content":
            cmd.extend(["-A", str(A)])
        if B is not None and output_mode == "content":
            cmd.extend(["-B", str(B)])
        if C is not None and output_mode == "content":
            cmd.extend(["-C", str(C)])

        # Set output mode
        if output_mode == "files_with_matches":
            cmd.append("-l")
        elif output_mode == "count":
            cmd.append("-c")
        # content mode is default, no flag needed

        # Add file type filter
        if type:
            cmd.extend(["-t", type])

        # Add glob filter
        if glob:
            cmd.extend(["-g", glob])

        # Execute ripgrep
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Handle ripgrep exit codes
        if result.returncode == 0:
            output_lines = (
                result.stdout.strip().split("\n") if result.stdout.strip() else []
            )
        elif result.returncode == 1:
            # No matches found
            return f"No matches found for pattern: {pattern}"
        else:
            # Error occurred
            error_msg = (
                result.stderr.strip()
                if result.stderr.strip()
                else "Unknown ripgrep error"
            )
            return f"Error in ripgrep search: {error_msg}"

        # Apply head limit if specified
        if head_limit and output_lines:
            output_lines = output_lines[:head_limit]

        return (
            "\n".join(output_lines)
            if output_lines
            else f"No matches found for pattern: {pattern}"
        )

    except subprocess.TimeoutExpired:
        return "Ripgrep search timed out after 30 seconds"
    except FileNotFoundError:
        return "Error: ripgrep (rg) not found. Please install ripgrep first."
    except Exception as e:
        return f"Error in grep search: {str(e)}"
