"""Command execution and shell management tools."""

import os
import re
import select
import subprocess
import time
import uuid
from langchain_core.tools import tool
from typing import List, TypedDict, Annotated

from colorama import Fore

from ..core.config import Config
from ..core.shell_manager import shell_manager


@tool("Bash")
def run_command(
    command: Annotated[str, "The command to execute"],
    timeout: Annotated[int, "Optional timeout in milliseconds (max 600000)"] = 120000,
    description: Annotated[
        str,
        " Clear, concise description of what this command does in 5-10 words. Examples:\nInput: ls\nOutput: Lists files in current directory\n\nInput: git status\nOutput: Shows working tree status\n\nInput: npm install\nOutput: Installs package dependencies\n\nInput: mkdir foo\nOutput: Creates directory 'foo'",
    ] = "",
    run_in_background: Annotated[
        bool,
        "Set to true to run this command in the background. Use BashOutput to read the output later.",
    ] = False,
) -> str:
    """Executes a given bash command in a persistent shell session with optional timeout, ensuring proper handling and security measures.

    Before executing the command, please follow these steps:

    1. Directory Verification:
       - If the command will create new directories or files, first use the LS tool to verify the parent directory exists and is the correct location
       - For example, before running "mkdir foo/bar", first use LS to check that "foo" exists and is the intended parent directory

    2. Command Execution:
       - Always quote file paths that contain spaces with double quotes (e.g., cd "path with spaces/file.txt")
       - Examples of proper quoting:
         - cd "/Users/name/My Documents" (correct)
         - cd /Users/name/My Documents (incorrect - will fail)
         - python "/path/with spaces/script.py" (correct)
         - python /path/with spaces/script.py (incorrect - will fail)
       - After ensuring proper quoting, execute the command.
       - Capture the output of the command.

    Usage notes:
      - The command argument is required.
      - You can specify an optional timeout in milliseconds (up to 600000ms / 10 minutes). If not specified, commands will timeout after 120000ms (2 minutes).
      - It is very helpful if you write a clear, concise description of what this command does in 5-10 words.
      - If the output exceeds 30000 characters, output will be truncated before being returned to you.
      - You can use the `run_in_background` parameter to run the command in the background, which allows you to continue working while the command runs. You can monitor the output using the Bash tool as it becomes available. Never use `run_in_background` to run 'sleep' as it will return immediately. You do not need to use '&' at the end of the command when using this parameter.
      - VERY IMPORTANT: You MUST avoid using search commands like `find` and `grep`. Instead use Grep, Glob, or Task to search. You MUST avoid read tools like `cat`, `head`, `tail`, and `ls`, and use Read and LS to read files.
     - If you _still_ need to run `grep`, STOP. ALWAYS USE ripgrep at `rg` first, which all Claude Code users have pre-installed.
      - When issuing multiple commands, use the ';' or '&&' operator to separate them. DO NOT use newlines (newlines are ok in quoted strings).
      - Try to maintain your current working directory throughout the session by using absolute paths and avoiding usage of `cd`. You may use `cd` if the User explicitly requests it.
        <good-example>
        pytest /foo/bar/tests
        </good-example>
        <bad-example>
        cd /foo/bar && pytest tests
        </bad-example>


    # Committing changes with git

    When the user asks you to create a new git commit, follow these steps carefully:

    1. You have the capability to call multiple tools in a single response. When multiple independent pieces of information are requested, batch your tool calls together for optimal performance. ALWAYS run the following bash commands in parallel, each using the Bash tool:
      - Run a git status command to see all untracked files.
      - Run a git diff command to see both staged and unstaged changes that will be committed.
      - Run a git log command to see recent commit messages, so that you can follow this repository's commit message style.
    2. Analyze all staged changes (both previously staged and newly added) and draft a commit message:
      - Summarize the nature of the changes (eg. new feature, enhancement to an existing feature, bug fix, refactoring, test, docs, etc.). Ensure the message accurately reflects the changes and their purpose (i.e. "add" means a wholly new feature, "update" means an enhancement to an existing feature, "fix" means a bug fix, etc.).
      - Check for any sensitive information that shouldn't be committed
      - Draft a concise (1-2 sentences) commit message that focuses on the "why" rather than the "what"
      - Ensure it accurately reflects the changes and their purpose
    3. You have the capability to call multiple tools in a single response. When multiple independent pieces of information are requested, batch your tool calls together for optimal performance. ALWAYS run the following commands in parallel:
       - Add relevant untracked files to the staging area.
       - Create the commit with a message ending with:
       🤖 Generated with [Claude Code](https://claude.ai/code)

       Co-Authored-By: Claude <noreply@anthropic.com>
       - Run git status to make sure the commit succeeded.
    4. If the commit fails due to pre-commit hook changes, retry the commit ONCE to include these automated changes. If it fails again, it usually means a pre-commit hook is preventing the commit. If the commit succeeds but you notice that files were modified by the pre-commit hook, you MUST amend your commit to include them.

    Important notes:
    - NEVER update the git config
    - NEVER run additional commands to read or explore code, besides git bash commands
    - NEVER use the TodoWrite or Task tools
    - DO NOT push to the remote repository unless the user explicitly asks you to do so
    - IMPORTANT: Never use git commands with the -i flag (like git rebase -i or git add -i) since they require interactive input which is not supported.
    - If there are no changes to commit (i.e., no untracked files and no modifications), do not create an empty commit
    - In order to ensure good formatting, ALWAYS pass the commit message via a HEREDOC, a la this example:
    <example>
    git commit -m "$(cat <<'EOF'
       Commit message here.

       🤖 Generated with [Claude Code](https://claude.ai/code)

       Co-Authored-By: Claude <noreply@anthropic.com>
       EOF
       )"
    </example>

    # Creating pull requests
    Use the gh command via the Bash tool for ALL GitHub-related tasks including working with issues, pull requests, checks, and releases. If given a Github URL use the gh command to get the information needed.

    IMPORTANT: When the user asks you to create a pull request, follow these steps carefully:

    1. You have the capability to call multiple tools in a single response. When multiple independent pieces of information are requested, batch your tool calls together for optimal performance. ALWAYS run the following bash commands in parallel using the Bash tool, in order to understand the current state of the branch since it diverged from the main branch:
       - Run a git status command to see all untracked files
       - Run a git diff command to see both staged and unstaged changes that will be committed
       - Check if the current branch tracks a remote branch and is up to date with the remote, so you know if you need to push to the remote
       - Run a git log command and `git diff [base-branch]...HEAD` to understand the full commit history for the current branch (from the time it diverged from the base branch)
    2. Analyze all changes that will be included in the pull request, making sure to look at all relevant commits (NOT just the latest commit, but ALL commits that will be included in the pull request!!!), and draft a pull request summary
    3. You have the capability to call multiple tools in a single response. When multiple independent pieces of information are requested, batch your tool calls together for optimal performance. ALWAYS run the following commands in parallel:
       - Create new branch if needed
       - Push to remote with -u flag if needed
       - Create PR using gh pr create with the format below. Use a HEREDOC to pass the body to ensure correct formatting.
    <example>
    gh pr create --title "the pr title" --body "$(cat <<'EOF'
    ## Summary
    <1-3 bullet points>

    ## Test plan
    [Checklist of TODOs for testing the pull request...]

    🤖 Generated with [Claude Code](https://claude.ai/code)
    EOF
    )"
    </example>

    Important:
    - NEVER update the git config
    - DO NOT use the TodoWrite or Task tools
    - Return the PR URL when you're done, so the user can see it

    # Other common operations
    - View comments on a Github PR: gh api repos/foo/bar/pulls/123/comments


    Args:
        command (str): The command to execute
        timeout (int, optional): Optional timeout in milliseconds (max 600000)
        description (str, optional): Clear, concise description of what this command does in 5-10 words. Examples:
    Input: ls
    Output: Lists files in current directory

    Input: git status
    Output: Shows working tree status

    Input: npm install
    Output: Installs package dependencies

    Input: mkdir foo
    Output: Creates directory 'foo'
        run_in_background (bool, optional): Set to true to run this command in the background. Use BashOutput to read the output later.

    Returns:
        str: Command output and status
    """
    try:
        timeout_seconds = min(
            timeout / 1000, 600
        )  # Convert ms to seconds, cap at 10 minutes

        # Reset cancellation flag
        shell_manager.reset_cancellation()

        # Enhanced git operation guidance
        def provide_git_guidance(cmd: str) -> str:
            """Provide helpful guidance for git operations"""
            guidance = ""
            cmd_lower = cmd.lower().strip()

            if cmd_lower.startswith("git commit"):
                if "-m" not in cmd_lower and not cmd_lower.endswith("--amend"):
                    guidance += "\n💡 Git Guidance: Consider running 'git status' and 'git diff --cached' first to review staged changes"
            elif cmd_lower.startswith("git push"):
                guidance += "\n💡 Git Guidance: Ensure all changes are committed and consider 'git log --oneline' to verify commits"
            elif cmd_lower.startswith("git merge") or cmd_lower.startswith(
                "git rebase"
            ):
                guidance += "\n💡 Git Guidance: Make sure working directory is clean with 'git status' before merge/rebase"
            elif cmd_lower == "git status":
                guidance += "\n💡 Git Guidance: This shows staged/unstaged changes - consider 'git diff' for detailed changes"
            elif cmd_lower.startswith("git add"):
                guidance += (
                    "\n💡 Git Guidance: Review changes with 'git diff' before staging"
                )

            return guidance

        if run_in_background:
            # Start background process
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )

            # Generate unique shell ID
            shell_id = str(uuid.uuid4())[:8]

            # Store background shell info
            shell_info = {
                "process": process,
                "command": command,
                "started_at": time.time(),
                "output_buffer": "",  # Store accumulated output
                "last_position": 0,  # Track what we've already returned
            }
            shell_manager.add_shell(shell_id, shell_info)

            return f"Background shell started with ID: {shell_id}\nCommand: {command}\nUse BashOutput tool with bash_id='{shell_id}' to monitor output."

        else:
            # Run synchronously with cancellation support
            shell_manager.current_process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            try:
                # Wait for process with timeout, checking for cancellation
                stdout, stderr = shell_manager.current_process.communicate(
                    timeout=timeout_seconds
                )
                result_code = shell_manager.current_process.returncode
                shell_manager.current_process = None

                # Check if cancelled
                if shell_manager.cancellation_requested:
                    return f"{Fore.YELLOW}⚠️  Command cancelled by user (Esc pressed)"

            except subprocess.TimeoutExpired:
                shell_manager.current_process.terminate()
                shell_manager.current_process.wait()
                shell_manager.current_process = None
                return f"Command timed out after {timeout_seconds} seconds"

            output = ""
            if stdout:
                output += stdout
            if stderr:
                output += f"\nSTDERR:\n{stderr}"
            if result_code != 0:
                output += f"\nReturn code: {result_code}"

            # Truncate if too long
            if len(output) > Config.MAX_OUTPUT_LENGTH:
                output = output[: Config.MAX_OUTPUT_LENGTH] + "\n[Output truncated...]"

            # Add git guidance if applicable
            git_guidance = provide_git_guidance(command)
            final_output = (
                output if output else "Command executed successfully (no output)"
            )

            return final_output + git_guidance

    except subprocess.TimeoutExpired:
        return f"Command timed out after {timeout_seconds} seconds"
    except Exception as e:
        return f"Error executing command: {str(e)}"


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
    shell_info = shell_manager.get_shell(bash_id)
    if not shell_info:
        return f"Background shell with ID '{bash_id}' not found. Available shells: {shell_manager.list_shells()}"
    process = shell_info["process"]

    try:
        # Check if process is still running
        if process.poll() is None:
            # Calculate runtime
            runtime = time.time() - shell_info.get("started_at", 0)
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
                current_buffer = shell_info.get("output_buffer", "")
                last_position = shell_info.get("last_position", 0)

                # Try non-blocking read if data is available
                if hasattr(select, "select") and process.stdout:
                    ready, _, _ = select.select([process.stdout], [], [], 0.1)
                    if ready:
                        try:
                            # Read available data in chunks to avoid blocking
                            import fcntl

                            fd = process.stdout.fileno()
                            fl = fcntl.fcntl(fd, fcntl.F_GETFL)
                            fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

                            try:
                                chunk = process.stdout.read(4096)
                                if chunk:
                                    current_buffer += chunk.decode(
                                        "utf-8", errors="ignore"
                                    )
                                    shell_info["output_buffer"] = current_buffer
                            except (BlockingIOError, OSError):
                                pass  # No data available right now
                            finally:
                                fcntl.fcntl(
                                    fd, fcntl.F_SETFL, fl
                                )  # Restore blocking mode

                        except (ImportError, AttributeError, OSError):
                            # Fallback for systems without fcntl
                            pass

                # Return only NEW output since last check
                new_output = current_buffer[last_position:]
                shell_info["last_position"] = len(current_buffer)

                # If no new output, provide status
                if not new_output.strip():
                    runtime = time.time() - shell_info.get("started_at", 0)
                    new_output = f"[Running for {runtime:.1f}s, PID: {process.pid}] No new output yet..."

            except Exception as e:
                # Fallback to basic status
                runtime = time.time() - shell_info.get("started_at", 0)
                new_output = f"Process running (PID: {process.pid}, {runtime:.1f}s). Error getting output: {str(e)}"

        # Apply filter if provided
        if filter and new_output:
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


# TodoItem type definition for the TodoWrite tool
class TodoItem(TypedDict):
    content: str
    status: str  # "pending", "in_progress", or "completed"
    id: str


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
