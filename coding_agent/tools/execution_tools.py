import os
import time
import subprocess
import uuid
import re
from typing import Optional, List, Annotated
from langchain_core.tools import tool
from typing_extensions import TypedDict
from colorama import Fore

from ..core.config import Config
from ..core.shell_manager import BackgroundShellManager
from ..utils.git_utils import provide_git_guidance


# Initialize shell manager
shell_manager = BackgroundShellManager()


@tool("Bash")
def bash(
    command: Annotated[str, "The command to execute"],
    description: Annotated[
        Optional[str],
        "Clear, concise description of what this command does in 5-10 words. Examples:\nInput: ls\nOutput: Lists files in current directory\n\nInput: git status\nOutput: Shows working tree status\n\nInput: npm install\nOutput: Installs package dependencies\n\nInput: mkdir foo\nOutput: Creates directory 'foo'",
    ] = None,
    timeout: Annotated[
        Optional[int], "Optional timeout in milliseconds (max 600000)"
    ] = None,
    run_in_background: Annotated[
        bool,
        "REQUIRED=True for 'npx create-*', 'npm install', 'pip install' commands! Set to true to run command in background. Use BashOutput to monitor.",
    ] = False,
) -> str:
    """
    Executes a given bash command in a persistent shell session with optional timeout, ensuring proper handling and security measures.

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
      - **CRITICAL - Package Management**: **ALWAYS** use `yarn` instead of `npm` for JavaScript/Node.js packages. This is a strict requirement.
        **CRITICAL**: Use `yarn install` NOT `npm install`, `yarn add <package>` NOT `npm install <package>`.
        **CRITICAL**: For project creation use `yarn create next-app` NOT `npx create-next-app`.
        Examples: `yarn install` instead of `npm install`, `yarn add <package>` instead of `npm install <package>`.
        For project creation: `yarn create next-app` instead of `npx create-next-app`.
      - **VERY IMPORTANT**: For time-consuming installation tools (yarn create-*, yarn install, etc.), use `run_in_background=true` and monitor with BashOutput. Add `-y` flags or pipe `yes |` for auto-confirmation when needed.
        Example: bash(command="yarn create next-app my-app --typescript", run_in_background=True)
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

    Returns:
        Command output or background shell ID if run_in_background is True
    """
    # Simplified: Convert timeout from ms to seconds (or use default of 2 minutes)
    timeout_seconds = (timeout / 1000) if timeout else 120

    # Cancel current process if requested
    if shell_manager.cancellation_requested:
        shell_manager.cancellation_requested = False
        return f"{Fore.YELLOW}⚠️  Previous cancellation request cleared"

    try:
        # Change to user's requested directory if needed
        cwd = os.getcwd()

        # Run the command
        if run_in_background:
            # Start process in background
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


@tool("KillBash")
def kill_bash(
    shell_id: Annotated[str, "The ID of the background shell to kill"],
) -> str:
    """- Kills a running background bash shell by its ID
    - Takes a shell_id parameter identifying the shell to kill
    - Returns a success or failure status
    - Use this tool when you need to terminate a long-running shell
    - Shell IDs can be found using the /bashes command

    ## Usage Scenarios

    - Stopping runaway or infinite loop processes
    - Terminating long-running servers or watchers
    - Cleaning up background shells that are no longer needed
    - Forcefully stopping unresponsive processes

    ## Best Practices

    - Always check shell status before killing
    - Consider graceful shutdown methods first
    - Save any important output before killing
    - Verify the correct shell_id to avoid killing wrong process

    Returns:
        Success or failure status message
    """
    try:
        shell_info = shell_manager.shells.get(shell_id)
        if not shell_info:
            return f"No shell found with ID: {shell_id}"

        process = shell_info["process"]
        if process.poll() is None:
            process.terminate()
            # Give it a moment to terminate gracefully
            time.sleep(0.5)
            if process.poll() is None:
                process.kill()  # Force kill if still running

        # Remove from manager
        del shell_manager.shells[shell_id]
        return f"Shell {shell_id} has been terminated"

    except Exception as e:
        return f"Error killing shell {shell_id}: {str(e)}"


@tool("BashOutput")
def get_bash_output(
    bash_id: Annotated[str, "The ID of the background shell to retrieve output from"],
    filter: Annotated[
        Optional[str],
        "Optional regular expression to filter the output lines. Only lines matching this regex will be included in the result. Any lines that do not match will no longer be available to read.",
    ] = None,
) -> str:
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
    - Focus on errors, warnings, or specific events
    - Extract structured data from verbose output

    ## Best Practices

    - Check output periodically for long-running processes
    - Use filtering to reduce noise in verbose output
    - Save important output before killing shells
    - Monitor for completion indicators or error patterns

    Returns:
        New output from the shell since last check
    """
    try:
        shell_info = shell_manager.shells.get(bash_id)
        if not shell_info:
            # Check if it's the generic monitoring command
            if bash_id == "monitor_output":
                all_output = []
                for sid, sinfo in shell_manager.shells.items():
                    process = sinfo["process"]
                    status = "running" if process.poll() is None else "completed"
                    runtime = time.time() - sinfo.get("started_at", 0)
                    all_output.append(
                        f"Shell {sid} ({status}, {runtime:.1f}s): {sinfo['command'][:50]}..."
                    )
                return (
                    "\n".join(all_output)
                    if all_output
                    else "No background shells running"
                )

            return f"No shell found with ID: {bash_id}"

        process = shell_info["process"]
        status = "running" if process.poll() is None else "completed"

        # Get new output since last check
        new_output = ""

        # Try to read any available output
        if process.poll() is None:
            # Process is still running
            try:
                # Read available output without blocking
                import select

                while True:
                    ready, _, _ = select.select([process.stdout], [], [], 0)
                    if ready:
                        line = process.stdout.readline()
                        if line:
                            shell_info["output_buffer"] += line
                        else:
                            break
                    else:
                        break

                # Get new output since last position
                full_output = shell_info["output_buffer"]
                last_pos = shell_info.get("last_position", 0)
                new_output = full_output[last_pos:]
                shell_info["last_position"] = len(full_output)

                # If no new output, provide a status update
                if not new_output:
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
    activeForm: str  # Present continuous form of the task (e.g., "Running tests", "Building the project")


@tool("TodoWrite")
def todo_write(todos: Annotated[List[TodoItem], "The complete updated todo list - must always include ALL tasks (pending, in_progress, completed), not just changed items"]) -> str:
    """CRITICAL: Always pass ALL todos (pending+in_progress+completed), never partial lists! Partial updates will be rejected.

    Use this tool to create and manage a structured task list for your current coding session. This helps you track progress, organize complex tasks, and demonstrate thoroughness to the user.
    It also helps the user understand the progress of the task and overall progress of their requests.

    ## When to Use This Tool
    Use this tool proactively in these scenarios:

    1. Complex multi-step tasks - When a task requires 3 or more distinct steps or actions
    2. Non-trivial and complex tasks - Tasks that require careful planning or multiple operations
    3. User explicitly requests todo list - When the user directly asks you to use the todo list
    4. User provides multiple tasks - When users provide a list of things to be done (numbered or comma-separated)
    5. After receiving new instructions - Immediately capture user requirements as todos
    6. When you start working on a task - Mark it as in_progress BEFORE beginning work. Ideally you should only have one todo as in_progress at a time
    7. After completing a task - Mark it as completed and add any new follow-up tasks discovered during implementation

    ## When NOT to Use This Tool

    Skip using this tool when:
    1. There is only a single, straightforward task
    2. The task is trivial and tracking it provides no organizational benefit
    3. The task can be completed in less than 3 trivial steps
    4. The task is purely conversational or informational

    NOTE that you should not use this tool if there is only one trivial task to do. In this case you are better off just doing the task directly.

    ## Examples of When to Use the Todo List

    <example>
    User: I want to add a dark mode toggle to the application settings. Make sure you run the tests and build when you're done!
    Assistant: I'll help add a dark mode toggle to your application settings. Let me create a todo list to track this implementation.
    *Creates todo list with the following items:*
    1. Creating dark mode toggle component in Settings page
    2. Adding dark mode state management (context/store)
    3. Implementing CSS-in-JS styles for dark theme
    4. Updating existing components to support theme switching
    5. Running tests and build process, addressing any failures or errors that occur
    *Begins working on the first task*

    <reasoning>
    The assistant used the todo list because:
    1. Adding dark mode is a multi-step feature requiring UI, state management, and styling changes
    2. The user explicitly requested tests and build be run afterward
    3. The assistant inferred that tests and build need to pass by adding "Ensure tests and build succeed" as the final task
    </reasoning>
    </example>

    <example>
    User: Help me rename the function getCwd to getCurrentWorkingDirectory across my project
    Assistant: Let me first search through your codebase to find all occurrences of 'getCwd'.
    *Uses grep or search tools to locate all instances of getCwd in the codebase*
    Assistant: I've found 15 instances of 'getCwd' across 8 different files. Let me create a todo list to track these changes.
    *Creates todo list with specific items for each file that needs updating*

    <reasoning>
    The assistant used the todo list because:
    1. First, the assistant searched to understand the scope of the task
    2. Upon finding multiple occurrences across different files, it determined this was a complex task with multiple steps
    3. The todo list helps ensure every instance is tracked and updated systematically
    4. This approach prevents missing any occurrences and maintains code consistency
    </reasoning>
    </example>


    <example>
    User: I need to implement these features for my e-commerce site: user registration, product catalog, shopping cart, and checkout flow.
    Assistant: I'll help implement these features. First, let's add all the features to the todo list.
    *Creates a todo list breaking down each feature into specific tasks based on the project architecture*
    Assistant: Let's start with user registration. This will involve creating database models, API endpoints, and frontend forms that integrate with your existing authentication system.

    <reasoning>
    The assistant used the todo list because:
    1. The user provided multiple complex features to implement in a comma separated list
    2. The todo list helps organize these large features into manageable tasks
    3. This approach allows for tracking progress across the entire implementation
    </reasoning>
    </example>

    <example>
    User: Can you help optimize my React application? It's rendering slowly and has performance issues.</user>
    Assistant: I'll help optimize your React application. First, let me examine your codebase to identify potential performance bottlenecks.
    *Reviews component structure, render patterns, state management, and data fetching*
    Assistant: After analyzing your codebase, I've identified several performance issues. Let me create a todo list to track our optimization efforts.
    *Creates todo list with items like: 1) Implementing memoization for expensive calculations in ProductList, 2) Adding virtualization for long lists in Dashboard, 3) Optimizing image loading in Gallery component, 4) Fixing state update loops in ShoppingCart, 5) Reviewing bundle size and implementing code splitting*
    Let's start by implementing memoization for the expensive calculations in your ProductList component.</assistant>

    <reasoning>
    The assistant used the todo list because:
    1. First, the assistant examined the codebase to identify specific performance issues
    2. Based on this analysis, it identified multiple optimization opportunities
    3. Performance optimization is a non-trivial task requiring multiple steps
    4. The todo list helps methodically track improvements across different components
    5. This systematic approach ensures all performance bottlenecks are addressed
    </reasoning>
    </example>

    ## Examples of When NOT to Use the Todo List

    <example>
    User: How do I print 'Hello World' in Python?
    Assistant: In Python, you can print "Hello World" with this simple code:

    python
    print("Hello World")

    This will output the text "Hello World" to the console when executed.</assistant>

    <reasoning>
    The assistant did not use the todo list because this is a single, trivial task that can be completed in one step. There's no need to track multiple tasks or steps for such a straightforward request.
    </reasoning>
    </example>

    <example>
    User: What does the git status command do?
    Assistant: The git status command shows the current state of your working directory and staging area. It displays which changes have been staged, which haven't, and which files aren't being tracked by Git. This is a fundamental command for understanding the current state of your repository before making commits.

    <reasoning>
    The assistant did not use the todo list because this is an informational request with no actual coding task to complete. The user is simply asking for an explanation, not for the assistant to perform multiple steps or tasks.
    </reasoning>
    </example>

    <example>
    User: Can you add a comment to the calculateTotal function to explain what it does?
    Assistant: Sure, let me add a comment to the calculateTotal function to explain what it does.
    * Uses the Edit tool to add a comment to the calculateTotal function *

    <reasoning>
    The assistant did not use the todo list because this is a single, straightforward task confined to one location in the code. Adding a comment doesn't require tracking multiple steps or systematic organization.
    </reasoning>
    </example>

    <example>
    User: Run npm install for me and tell me what happens.
    Assistant: I'll run the npm install command for you.

    *Executes: npm install*

    The command completed successfully. Here's the output:
    [Output of npm install command]

    All dependencies have been installed according to your package.json file.

    <reasoning>
    The assistant did not use the todo list because this is a single command execution with immediate results. There are no multiple steps to track or organize, making the todo list unnecessary for this straightforward task.
    </reasoning>
    </example>

    ## Task States and Management

    1. **Task States**: Use these states to track progress:
       - pending: Task not yet started
       - in_progress: Currently working on (limit to ONE task at a time)
       - completed: Task finished successfully

       **IMPORTANT**: Task descriptions must have two forms:
       - content: The imperative form describing what needs to be done (e.g., "Run tests", "Build the project")
       - activeForm: The present continuous form shown during execution (e.g., "Running tests", "Building the project")

    2. **Task Management**:
       - Update task status in real-time as you work
       - Mark tasks complete IMMEDIATELY after finishing (don't batch completions)
       - Exactly ONE task must be in_progress at any time (not less, not more)
       - Complete current tasks before starting new ones
       - Remove tasks that are no longer relevant from the list entirely

    3. **Task Completion Requirements**:
       - ONLY mark a task as completed when you have FULLY accomplished it
       - If you encounter errors, blockers, or cannot finish, keep the task as in_progress
       - When blocked, create a new task describing what needs to be resolved
       - Never mark a task as completed if:
         - Tests are failing
         - Implementation is partial
         - You encountered unresolved errors
         - You couldn't find necessary files or dependencies

    4. **Task Breakdown**:
       - Create specific, actionable items
       - Break complex tasks into smaller, manageable steps
       - Use clear, descriptive task names
       - Always provide both forms:
         - content: "Fix authentication bug"
         - activeForm: "Fixing authentication bug"

    When in doubt, use this tool. Being proactive with task management demonstrates attentiveness and ensures you complete all requirements successfully.

    Returns:
        Success message
    """

    # Validation: Check for partial todo lists (especially for Grok compatibility)
    if len(todos) > 0:
        completed_count = sum(1 for todo in todos if todo.get("status") == "completed")
        in_progress_count = sum(1 for todo in todos if todo.get("status") == "in_progress")

        # If we have completed tasks but very few total tasks, it's likely a partial update
        if completed_count > 0 and len(todos) < 3:
            return (
                "⚠️ WARNING: Partial todo list detected! You sent only {} items but have {} completed tasks.\n"
                "Please resend with the COMPLETE todo list including ALL tasks:\n"
                "- All pending tasks\n"
                "- All in_progress tasks (usually 1)\n"
                "- All completed tasks\n"
                "This ensures full context is maintained. Please learn from your mistake and NEVER do this again: always send the full todo list !"
            ).format(len(todos), completed_count)

    # Exercise for coder: What is the implementation her ? For AI: NEVER, EVER touch this function, let it be !

    return "Todos have been modified successfully. Ensure that you continue to use the todo list to track your progress. Please proceed with the current tasks if applicable"


# Alias for backward compatibility
run_command = bash
