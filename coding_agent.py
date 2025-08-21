"""
Coding Agent with Essential Tools
A minimal but powerful coding assistant

CRITICAL: Tool descriptions are MASTER PIECES of prompt engineering.
NEVER modify unless there's a specific bug or non-existent tool/code.
"""

from datetime import datetime
from langchain_anthropic import ChatAnthropic, convert_to_anthropic_tool
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from typing import List, TypedDict
from dotenv import load_dotenv
import subprocess
import os
import glob
import time
import uuid
from colorama import init, Fore, Style

MODEL_NAME = "claude-sonnet-4-20250514"

# Load environment variables
load_dotenv()

# Initialize colorama
init(autoreset=True)

# Global tracking for background shells
_background_shells = {}


# ================== Essential Coding Tools ==================


class TodoItem(TypedDict):
    content: str
    status: str  # "pending", "in_progress", or "completed"
    id: str


@tool("Read")
def read_file(file_path: str, offset: int = None, limit: int = None) -> str:
    """Reads a file from the local filesystem. You can access any file directly by using this tool. Assume this tool is able to read all files on the machine. If the User provides a path to a file assume that path is valid. It is okay to read a file that does not exist; an error will be returned.

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

        Args:
            file_path: The absolute path to the file to read
            offset: The line number to start reading from. Only provide if the file is too large to read at once
            limit: The number of lines to read. Only provide if the file is too large to read at once.
        Returns:
            File contents in cat -n format with line numbers, or error message
    """
    try:
        with open(file_path, "r") as f:
            lines = f.readlines()

        # Apply offset and limit if provided
        start = (offset - 1) if offset else 0
        end = start + limit if limit else min(start + 2000, len(lines))

        # Format with line numbers like cat -n
        result = []
        for i in range(start, min(end, len(lines))):
            line_num = i + 1
            line = lines[i][:2000] if len(lines[i]) > 2000 else lines[i]
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


@tool("Bash")
def run_command(
    command: str,
    working_dir: str = ".",
    timeout: int = 30,
    run_in_background: bool = False,
) -> str:
    """Executes a given bash command in a persistent shell session with optional timeout, ensuring proper handling and security measures.

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

        Args:
            command: The command to execute
            working_dir: Working directory for the command (default: current)
            timeout: Timeout in seconds (default: 30, max: 600)
            run_in_background: Set to true to run this command in the background. Use BashOutput to read the output later.
        Returns:
            Command output (stdout + stderr) or error message, or background shell ID if run_in_background=True
    """
    try:
        timeout = min(timeout, 600)  # Cap at 10 minutes
        global _background_shells
        
        # Enhanced git operation guidance
        def provide_git_guidance(cmd: str) -> str:
            """Provide helpful guidance for git operations"""
            guidance = ""
            cmd_lower = cmd.lower().strip()
            
            if cmd_lower.startswith('git commit'):
                if '-m' not in cmd_lower and not cmd_lower.endswith('--amend'):
                    guidance += "\n💡 Git Guidance: Consider running 'git status' and 'git diff --cached' first to review staged changes"
            elif cmd_lower.startswith('git push'):
                guidance += "\n💡 Git Guidance: Ensure all changes are committed and consider 'git log --oneline' to verify commits"
            elif cmd_lower.startswith('git merge') or cmd_lower.startswith('git rebase'):
                guidance += "\n💡 Git Guidance: Make sure working directory is clean with 'git status' before merge/rebase"
            elif cmd_lower == 'git status':
                guidance += "\n💡 Git Guidance: This shows staged/unstaged changes - consider 'git diff' for detailed changes"
            elif cmd_lower.startswith('git add'):
                guidance += "\n💡 Git Guidance: Review changes with 'git diff' before staging"
                
            return guidance

        if run_in_background:
            # Start background process
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=working_dir,
                bufsize=1,
                universal_newlines=True,
            )

            # Generate unique shell ID
            shell_id = str(uuid.uuid4())[:8]

            # Store background shell info
            _background_shells[shell_id] = {
                "process": process,
                "command": command,
                "started_at": time.time(),
                "working_dir": working_dir,
                "output_buffer": "",  # Store accumulated output
                "last_position": 0,   # Track what we've already returned
            }

            return f"Background shell started with ID: {shell_id}\nCommand: {command}\nUse BashOutput tool with bash_id='{shell_id}' to monitor output."

        else:
            # Run synchronously as before
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=working_dir,
            )

            output = ""
            if result.stdout:
                output += result.stdout
            if result.stderr:
                output += f"\nSTDERR:\n{result.stderr}"
            if result.returncode != 0:
                output += f"\nReturn code: {result.returncode}"

            # Truncate if too long
            if len(output) > 30000:
                output = output[:30000] + "\n[Output truncated...]"

            # Add git guidance if applicable
            git_guidance = provide_git_guidance(command)
            final_output = output if output else "Command executed successfully (no output)"
            
            return final_output + git_guidance

    except subprocess.TimeoutExpired:
        return f"Command timed out after {timeout} seconds"
    except Exception as e:
        return f"Error executing command: {str(e)}"


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
    - Supports full regex syntax (e.g., `log.*Error`, `function\\s+\\w+`)
    - Filter files with glob parameter (e.g., `*.js`, `**/*.tsx`) or type parameter (e.g., `js`, `py`, `rust`)
    - Use Task tool for open-ended searches requiring multiple rounds
    - Pattern syntax: Uses ripgrep (not grep) - literal braces need escaping (use `interface\\{\\}` to find `interface{}` in Go code)
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
                os.path.expanduser("~/.cargo/bin/rg")
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
            output_lines = result.stdout.strip().split('\n') if result.stdout.strip() else []
        elif result.returncode == 1:
            # No matches found
            return f"No matches found for pattern: {pattern}"
        else:
            # Error occurred
            error_msg = result.stderr.strip() if result.stderr.strip() else "Unknown ripgrep error"
            return f"Error in ripgrep search: {error_msg}"
        
        # Apply head limit if specified
        if head_limit and output_lines:
            output_lines = output_lines[:head_limit]
        
        return '\n'.join(output_lines) if output_lines else f"No matches found for pattern: {pattern}"
        
    except subprocess.TimeoutExpired:
        return "Ripgrep search timed out after 30 seconds"
    except FileNotFoundError:
        return "Error: ripgrep (rg) not found. Please install ripgrep first."
    except Exception as e:
        return f"Error in grep search: {str(e)}"


@tool("TodoWrite")
def todo_write(todos: List[TodoItem]) -> str:
    """Use this tool to create and manage a structured task list for your current coding session. This helps you track progress, organize complex tasks, and demonstrate thoroughness to the user. It also helps the user understand the progress of the task and overall progress of their requests.

    ## When to Use This Tool

    Use this tool proactively in these scenarios:

    1. **Complex multi-step tasks** - When a task requires 3 or more distinct steps or actions
    2. **Non-trivial and complex tasks** - Tasks that require careful planning or multiple operations
    3. **User explicitly requests todo list** - When the user directly asks you to use the todo list
    4. **User provides multiple tasks** - When users provide a list of things to be done (numbered or comma-separated)
    5. **After receiving new instructions** - Immediately capture user requirements as todos
    6. **When you start working on a task** - Mark it as in_progress BEFORE beginning work. Ideally you should only have one todo as in_progress at a time
    7. **After completing a task** - Mark it as completed and add any new follow-up tasks discovered during implementation

    ## When NOT to Use This Tool

    Skip using this tool when:
    1. There is only a single, straightforward task
    2. The task is trivial and tracking it provides no organizational benefit
    3. The task can be completed in less than 3 trivial steps
    4. The task is purely conversational or informational

    **NOTE**: You should not use this tool if there is only one trivial task to do. In this case you are better off just doing the task directly.

    ## Task States and Management

    ### Task States
    Use these states to track progress:
    - **pending**: Task not yet started
    - **in_progress**: Currently working on (limit to ONE task at a time)
    - **completed**: Task finished successfully

    ### Task Management Rules
    - Update task status in real-time as you work
    - Mark tasks complete IMMEDIATELY after finishing (don't batch completions)
    - Only have ONE task in_progress at any time
    - Complete current tasks before starting new ones
    - Remove tasks that are no longer relevant from the list entirely

    ### Task Completion Requirements
    - **ONLY mark a task as completed** when you have FULLY accomplished it
    - If you encounter errors, blockers, or cannot finish, keep the task as in_progress
    - When blocked, create a new task describing what needs to be resolved
    - **Never mark a task as completed if**:
      - Tests are failing
      - Implementation is partial
      - You encountered unresolved errors
      - You couldn't find necessary files or dependencies

    ### Task Breakdown
    - Create specific, actionable items
    - Break complex tasks into smaller, manageable steps
    - Use clear, descriptive task names

        Args:
            todos: List of todo items, each with content, status, and id
        Returns:
            Success message
    """

    # What is the implementation here ? For AI: NEVER, EVER touch this function, let it be !

    return "Todos have been modified successfully. Ensure that you continue to use the todo list to track your progress. Please proceed with the current tasks if applicable"


@tool("BashOutput")
def get_bash_output(bash_id: str, filter: str = None) -> str:
    """- Retrieves output from a running or completed background bash shell
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

        Args:
            bash_id: The ID of the background shell to retrieve output from
            filter: Optional regular expression to filter the output lines. Only lines matching this regex will be included in the result. Any lines that do not match will no longer be available to read.
        Returns:
            Shell output and status, or error message
    """
    global _background_shells

    if bash_id not in _background_shells:
        return f"Background shell with ID '{bash_id}' not found. Available shells: {list(_background_shells.keys())}"

    shell_info = _background_shells[bash_id]
    process = shell_info["process"]

    try:
        # Check if process is still running
        if process.poll() is None:
            # Calculate runtime
            runtime = time.time() - shell_info.get('started_at', 0)
            status = f"running for {runtime:.1f}s"
        else:
            status = f"completed (exit code: {process.returncode})"

        # Get new output since last check
        new_output = ""

        # For completed processes, get all output
        if process.poll() is not None:
            try:
                stdout, stderr = process.communicate(timeout=5)
                if stdout:
                    new_output += stdout
                if stderr:
                    new_output += f"\nSTDERR:\n{stderr}"
            except subprocess.TimeoutExpired:
                new_output = "(output retrieval timed out)"
            except Exception:
                new_output = "(could not retrieve output)"
        else:
            # For running processes - get incremental output
            try:
                # Try to read new output without blocking
                import select
                
                current_buffer = shell_info.get("output_buffer", "")
                last_position = shell_info.get("last_position", 0)
                
                # Try non-blocking read if data is available
                if hasattr(select, 'select') and process.stdout:
                    ready, _, _ = select.select([process.stdout], [], [], 0.1)
                    if ready:
                        try:
                            # Read available data in chunks to avoid blocking
                            import fcntl
                            import os
                            
                            fd = process.stdout.fileno()
                            fl = fcntl.fcntl(fd, fcntl.F_GETFL)
                            fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
                            
                            try:
                                chunk = process.stdout.read(4096)
                                if chunk:
                                    current_buffer += chunk.decode('utf-8', errors='ignore')
                                    shell_info["output_buffer"] = current_buffer
                            except (BlockingIOError, OSError):
                                pass  # No data available right now
                            finally:
                                fcntl.fcntl(fd, fcntl.F_SETFL, fl)  # Restore blocking mode
                                
                        except (ImportError, AttributeError, OSError):
                            # Fallback for systems without fcntl
                            pass
                
                # Return only NEW output since last check
                new_output = current_buffer[last_position:]
                shell_info["last_position"] = len(current_buffer)
                
                # If no new output, provide status
                if not new_output.strip():
                    runtime = time.time() - shell_info.get('started_at', 0)
                    new_output = f"[Running for {runtime:.1f}s, PID: {process.pid}] No new output yet..."
                    
            except Exception as e:
                # Fallback to basic status
                runtime = time.time() - shell_info.get('started_at', 0)
                new_output = f"Process running (PID: {process.pid}, {runtime:.1f}s). Error getting output: {str(e)}"

        # Apply filter if provided
        if filter and new_output:
            import re

            try:
                regex = re.compile(filter)
                lines = new_output.split("\n")
                filtered_lines = [line for line in lines if regex.search(line)]
                new_output = "\n".join(filtered_lines)
            except re.error as e:
                return f"Invalid regex filter: {e}"

        if not new_output:
            new_output = "(no new output)"

        return f"Shell {bash_id} ({status}):\n{new_output}"

    except Exception as e:
        return f"Error retrieving output from shell {bash_id}: {str(e)}"


# ================== System Prompt ==================


def coding_agent_prompt():
    import platform

    today = datetime.now().strftime("%Y-%m-%d")
    os_info = f"{platform.system()} {platform.release()}"

    return f"""You are an interactive CLI tool that helps users with software engineering tasks. Use the instructions below and the tools available to you to assist the user.

IMPORTANT: Assist with defensive security tasks only. Refuse to create, modify, or improve code that may be used maliciously. Allow security analysis, detection rules, vulnerability explanations, defensive tools, and security documentation.
IMPORTANT: You must NEVER generate or guess URLs for the user unless you are confident that the URLs are for helping the user with programming. You may use URLs provided by the user in their messages or local files.

If the user asks for help or wants to give feedback inform them of the following: 
- /help: Get help with using Claude Code
- To give feedback, users should report the issue at https://github.com/anthropics/claude-code/issues

# Tone and style
You should be concise, direct, and to the point.
You MUST answer concisely with fewer than 4 lines (not including tool use or code generation), unless user asks for detail.
IMPORTANT: You should minimize output tokens as much as possible while maintaining helpfulness, quality, and accuracy. Only address the specific query or task at hand, avoiding tangential information unless absolutely critical for completing the request. If you can answer in 1-3 sentences or a short paragraph, please do.
IMPORTANT: You should NOT answer with unnecessary preamble or postamble (such as explaining your code or summarizing your action), unless the user asks you to.
Do not add additional code explanation summary unless requested by the user. After working on a file, just stop, rather than providing an explanation of what you did.
Answer the user's question directly, without elaboration, explanation, or details. One word answers are best. Avoid introductions, conclusions, and explanations. You MUST avoid text before/after your response, such as "The answer is <answer>.", "Here is the content of the file..." or "Based on the information provided, the answer is..." or "Here is what I will do next...". Here are some examples to demonstrate appropriate verbosity:

## Examples

**Example 1:**
user: 2 + 2
assistant: 4

**Example 2:**
user: what is 2+2?
assistant: 4

**Example 3:**
user: is 11 a prime number?
assistant: Yes

**Example 4:**
user: what command should I run to list files in the current directory?
assistant: ls

**Example 5:**
user: what command should I run to watch files in the current directory?
assistant: [runs ls to list the files in the current directory, then read docs/commands in the relevant file to find out how to watch files]
npm run dev

**Example 6:**
user: How many golf balls fit inside a jetta?
assistant: 150000

**Example 7:**
user: what files are in the directory src/?
assistant: [runs ls and sees foo.c, bar.c, baz.c]
user: which file contains the implementation of foo?
assistant: src/foo.c

When you run a non-trivial bash command, you should explain what the command does and why you are running it, to make sure the user understands what you are doing (this is especially important when you are running a command that will make changes to the user's system).
Remember that your output will be displayed on a command line interface. Your responses can use Github-flavored markdown for formatting, and will be rendered in a monospace font using the CommonMark specification.
Output text to communicate with the user; all text you output outside of tool use is displayed to the user. Only use tools to complete tasks. Never use tools like Bash or code comments as means to communicate with the user during the session.
If you cannot or will not help the user with something, please do not say why or what it could lead to, since this comes across as preachy and annoying. Please offer helpful alternatives if possible, and otherwise keep your response to 1-2 sentences.
Only use emojis if the user explicitly requests it. Avoid using emojis in all communication unless asked.
IMPORTANT: Keep your responses short, since they will be displayed on a command line interface.

# Proactiveness
You are allowed to be proactive, but only when the user asks you to do something. You should strive to strike a balance between:
- Doing the right thing when asked, including taking actions and follow-up actions
- Not surprising the user with actions you take without asking
For example, if the user asks you how to approach something, you should do your best to answer their question first, and not immediately jump into taking actions.

# Following conventions
When making changes to files, first understand the file's code conventions. Mimic code style, use existing libraries and utilities, and follow existing patterns.
- NEVER assume that a given library is available, even if it is well known. Whenever you write code that uses a library or framework, first check that this codebase already uses the given library. For example, you might look at neighboring files, or check the package.json (or cargo.toml, and so on depending on the language).
- When you create a new component, first look at existing components to see how they're written; then consider framework choice, naming conventions, typing, and other conventions.
- When you edit a piece of code, first look at the code's surrounding context (especially its imports) to understand the code's choice of frameworks and libraries. Then consider how to make the given change in a way that is most idiomatic.
- Always follow security best practices. Never introduce code that exposes or logs secrets and keys. Never commit secrets or keys to the repository.

# Code style
- IMPORTANT: DO NOT ADD ***ANY*** COMMENTS unless asked

# Task Management
You have access to the TodoWrite tools to help you manage and plan tasks. Use these tools VERY frequently to ensure that you are tracking your tasks and giving the user visibility into your progress.
These tools are also EXTREMELY helpful for planning tasks, and for breaking down larger complex tasks into smaller steps. If you do not use this tool when planning, you may forget to do important tasks - and that is unacceptable.

It is critical that you mark todos as completed as soon as you are done with a task. Do not batch up multiple tasks before marking them as completed.

## Examples

**Example 1:**
user: Run the build and fix any type errors
assistant: I'm going to use the TodoWrite tool to write the following items to the todo list: 
- Run the build
- Fix any type errors

I'm now going to run the build using Bash.

Looks like I found 10 type errors. I'm going to use the TodoWrite tool to write 10 items to the todo list.

marking the first todo as in_progress

Let me start working on the first item...

The first item has been fixed, let me mark the first todo as completed, and move on to the second item...
..
..

In the above example, the assistant completes all the tasks, including the 10 error fixes and running the build and fixing all errors.

**Example 2:**
user: Help me write a new feature that allows users to track their usage metrics and export them to various formats

assistant: I'll help you implement a usage metrics tracking and export feature. Let me first use the TodoWrite tool to plan this task.
Adding the following todos to the todo list:
1. Research existing metrics tracking in the codebase
2. Design the metrics collection system
3. Implement core metrics tracking functionality
4. Create export functionality for different formats

Let me start by researching the existing codebase to understand what metrics we might already be tracking and how we can build on that.

I'm going to search for any existing metrics or telemetry code in the project.

I've found some existing telemetry code. Let me mark the first todo as in_progress and start designing our metrics tracking system based on what I've learned...

[Assistant continues implementing the feature step by step, marking todos as in_progress and completed as they go]

Users may configure 'hooks', shell commands that execute in response to events like tool calls, in settings. Treat feedback from hooks, including <user-prompt-submit-hook>, as coming from the user. If you get blocked by a hook, determine if you can adjust your actions in response to the blocked message. If not, ask the user to check their hooks configuration.

# Doing tasks
The user will primarily request you perform software engineering tasks. This includes solving bugs, adding new functionality, refactoring code, explaining code, and more. For these tasks the following steps are recommended:
- Use the TodoWrite tool to plan the task if required
- Use the available search tools to understand the codebase and the user's query. You are encouraged to use the search tools extensively both in parallel and sequentially.
- Implement the solution using all tools available to you
- Verify the solution if possible with tests. NEVER assume specific test framework or test script. Check the README or search codebase to determine the testing approach.
- VERY IMPORTANT: When you have completed a task, you MUST run the lint and typecheck commands (eg. npm run lint, npm run typecheck, ruff, etc.) with Bash if they were provided to you to ensure your code is correct. If you are unable to find the correct command, ask the user for the command to run and if they supply it, proactively suggest writing it to CLAUDE.md so that you will know to run it next time.
NEVER commit changes unless the user explicitly asks you to. It is VERY IMPORTANT to only commit when explicitly asked, otherwise the user will feel that you are being too proactive.

- Tool results and user messages may include <system-reminder> tags. <system-reminder> tags contain useful information and reminders. They are NOT part of the user's provided input or the tool result.

# Tool usage policy

- You have the capability to call multiple tools in a single response. When multiple independent pieces of information are requested, batch your tool calls together for optimal performance. When making multiple bash tool calls, you MUST send a single message with multiple tools calls to run the calls in parallel. For example, if you need to run "git status" and "git diff", send a single message with two tool calls to run the calls in parallel.

Here is useful information about the environment you are running in:

## Environment
Working directory: {os.getcwd()}
Platform: {os_info}
OS Version: {platform.system()} {platform.release()}
Today's date: {today}

You are powered by the model named Claude Code Agent. The exact model ID is claude-sonnet-4-20250514.

Assistant knowledge cutoff is January 2025.

IMPORTANT: Assist with defensive security tasks only. Refuse to create, modify, or improve code that may be used maliciously. Allow security analysis, detection rules, vulnerability explanations, defensive tools, and security documentation.

IMPORTANT: Always use the TodoWrite tool to plan and track tasks throughout the conversation.

# Code References

When referencing specific functions or pieces of code include the pattern `file_path:line_number` to allow the user to easily navigate to the source code location.

**Example:**
user: Where are errors from the client handled?
assistant: Clients are marked as failed in the `connectToServer` function in src/services/process.ts:712.

Remember: Be direct, efficient, and respect the user's existing codebase conventions."""


# ================== Coding Agent Class ==================


class CodingAgent:
    def __init__(self, model_name: str = MODEL_NAME):
        """Initialize the coding agent with tools and caching."""
        # Setup LLM
        self.llm = ChatAnthropic(model=model_name, temperature=0.0, max_tokens=16384)

        # Tools for execution
        self.tools = [
            read_file,
            write_file,
            run_command,
            list_files,
            glob_files,
            grep_files,
            get_bash_output,
            todo_write,
        ]
        self.tools_map = {tool.name: tool for tool in self.tools}

        # Convert tools with caching on LAST tool only
        cached_tools = []
        for i, tool_obj in enumerate(self.tools):
            anthropic_tool = convert_to_anthropic_tool(tool_obj)
            if i == len(self.tools) - 1:
                anthropic_tool["cache_control"] = {"type": "ephemeral"}
            cached_tools.append(anthropic_tool)

        # Bind tools
        self.llm_with_tools = self.llm.bind_tools(cached_tools)

        # System prompt with tools description
        tools_desc = "\n\nAvailable tools:\n"
        for t in self.tools:
            tools_desc += f"- {t.name}: {t.description}\n"

        # self.system_prompt_str = coding_agent_prompt() + tools_desc
        self.system_prompt_str = coding_agent_prompt() + tools_desc

        # Initialize messages with cached system prompt
        self.messages: List = [
            SystemMessage(
                content=[
                    {
                        "type": "text",
                        "text": self.system_prompt_str,
                        "cache_control": {"type": "ephemeral"},
                    }
                ]
            )
        ]

        self.working_dir = "."

    def chat(self, user_input: str) -> str:
        """Process user coding request."""
        # Add user message with cache control
        self.messages.append(
            HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": user_input,
                        "cache_control": {"type": "ephemeral"},
                    }
                ]
            )
        )

        # Get initial response
        response = self.llm_with_tools.invoke(self.messages)

        print(Fore.CYAN + "=" * 50)
        print(Fore.GREEN + "🤖 Initial response: " + Style.RESET_ALL, response)

        print(Fore.YELLOW + "=" * 20)
        usage = response.response_metadata.get("usage", {})
        print(
            Fore.BLUE + f"📊 Tokens - Input: {usage.get('input_tokens', 0)} "
            f"(cached: {usage.get('cache_read_input_tokens', 0)}) "
            f"Output: {usage.get('output_tokens', 0)}"
        )
        print(Fore.YELLOW + "=" * 20)

        # Remove cache_control from user message
        self.messages[-1].content[0].pop("cache_control", None)

        # Add response
        self.messages.append(response)

        # Handle tool calls
        while hasattr(response, "tool_calls") and response.tool_calls:
            print(
                Fore.MAGENTA + f"\n🔧 Executing {len(response.tool_calls)} tool(s)..."
            )

            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]

                # Special handling for run_command to use working_dir
                if tool_name == "run_command" and "working_dir" not in tool_args:
                    tool_args["working_dir"] = self.working_dir

                print(Fore.CYAN + "\n🔧 TOOL CALL DEBUG:")
                print(Fore.WHITE + f"   📝 Name: {tool_name}")
                print(Fore.WHITE + f"   ⚙️  Parameters: {tool_args}")

                # Execute tool
                if tool_name in self.tools_map:
                    tool_result = self.tools_map[tool_name].invoke(tool_args)
                else:
                    tool_result = f"Unknown tool: {tool_name}"

                print(
                    Fore.GREEN
                    + f"   ✅ Result (first 500 chars): {str(tool_result)[:500]}..."
                )
                print(
                    Fore.BLUE
                    + f"   📏 Result length: {len(str(tool_result))} characters"
                )
                print(Fore.CYAN + "=" * 50)

                # Add tool result
                self.messages.append(
                    ToolMessage(
                        content=str(tool_result)[:5000],  # Limit size
                        tool_call_id=tool_call["id"],
                    )
                )

            # add cache_control
            last_message = self.messages[-1]
            self.messages[-1].content = [
                {
                    "type": "text",
                    "text": last_message.content,
                    "cache_control": {"type": "ephemeral"},
                }
            ]
            response = self.llm_with_tools.invoke(self.messages)
            # remove cache_control mark for reuse later on
            self.messages[-1].content[0].pop("cache_control", None)

            self.messages.append(response)
            usage = response.response_metadata.get("usage", {})
            print(
                Fore.BLUE + f"📊 After tools - Input: {usage.get('input_tokens', 0)} "
                f"(cached: {usage.get('cache_read_input_tokens', 0)})"
            )

        return response.content

    def set_working_dir(self, directory: str):
        """Set the working directory for commands."""
        self.working_dir = directory
        print(Fore.GREEN + f"📁 Working directory set to: {directory}")

    def reset(self):
        """Reset conversation but keep cached system prompt."""
        self.messages = [self.messages[0]]
        print(Fore.YELLOW + "🔄 Conversation reset (keeping cached system prompt)")


# ================== Demo & Interactive Mode ==================


def demo():
    """Demo the coding agent."""
    print(Fore.CYAN + "\n" + "=" * 70)
    print(Fore.GREEN + "🚀 DEMO: Coding Agent")
    print(Fore.CYAN + "=" * 70)

    agent = CodingAgent()

    # Demo tasks
    tasks = [
        "List all Python files in the current directory",
        "Create a simple hello_world.py file that prints 'Hello from Coding Agent!'",
        "Run the hello_world.py file we just created",
        "Create a fibonacci.py with a function to calculate fibonacci numbers, then test it",
    ]

    for i, task in enumerate(tasks, 1):
        print(Fore.YELLOW + f"\n📝 Task {i}: {task}")
        response = agent.chat(task)
        print(Fore.GREEN + f"\n✅ Response: {response[:500]}...")

        if i < len(tasks):
            input(Fore.WHITE + "\nPress Enter for next task...")

    print(Fore.CYAN + "\n" + "=" * 70)
    print(Fore.GREEN + "🎉 Demo completed! Files created in current directory.")
    print(Fore.CYAN + "=" * 70)


def interactive():
    """Interactive coding session."""
    print(Fore.CYAN + "\n" + "=" * 70)
    print(Fore.GREEN + "🤖 Coding Agent - Interactive Mode")
    print(Fore.CYAN + "=" * 70)
    print(Fore.YELLOW + "\nCommands:")
    print(Fore.WHITE + "  'quit' - Exit")
    print(Fore.WHITE + "  'reset' - Clear conversation history")
    print(Fore.WHITE + "  'cd <dir>' - Change working directory")
    print(Fore.WHITE + "  'pwd' - Show current working directory")
    print(Fore.YELLOW + "\nYou can ask me to:")
    print(Fore.WHITE + "  - Read and analyze code")
    print(Fore.WHITE + "  - Write new files or modify existing ones")
    print(Fore.WHITE + "  - Run commands and scripts")
    print(Fore.WHITE + "  - Debug issues")
    print(Fore.WHITE + "  - Refactor code")
    print(Fore.WHITE + "  - Set up new projects")
    print(Fore.CYAN + "=" * 70 + "\n")

    agent = CodingAgent()

    while True:
        user_input = input(Fore.RED + "\n💻 You: " + Style.RESET_ALL)

        if user_input.lower() in ["quit", "exit"]:
            print(Fore.GREEN + "\n👋 Goodbye!\n")
            break

        if user_input.lower() == "reset":
            agent.reset()
            continue

        if user_input.lower() == "pwd":
            print(Fore.BLUE + f"📁 Current working directory: {agent.working_dir}")
            continue

        if user_input.lower().startswith("cd "):
            new_dir = user_input[3:].strip()
            if os.path.isdir(new_dir):
                agent.set_working_dir(new_dir)
            else:
                print(Fore.RED + f"❌ Directory not found: {new_dir}")
            continue

        try:
            response = agent.chat(user_input)
            print(Fore.GREEN + f"\n🤖 Agent: {response}")
        except Exception as e:
            print(Fore.RED + f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    interactive()
