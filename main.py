"""Main entry point and interactive interface for the coding agent."""

import os
from colorama import Fore, Style, init

from coding_agent.core.agent import CodingAgent

# Initialize colorama
init(autoreset=True)


# Initialize the customized agents system at startup
def initialize_agents_system():
    """Initialize the agents system with dynamic Task tool description."""
    try:
        from coding_agent.tools.task_tool import initialize_task_tool_description
        from coding_agent.core.agent_registry import AgentRegistry

        # Initialize agent registry (discovers available agents)
        registry = AgentRegistry()
        agent_count = registry.get_agent_count()

        print(
            Fore.CYAN + Style.DIM
            + f"🔧 Initializing agents system... Found {agent_count['total']} agents ({agent_count['built_in']} built-in, {agent_count['user_defined']} user-defined)"
        )

        # Initialize Task tool description based on available agents
        description = initialize_task_tool_description()

        print(
            Fore.GREEN + Style.DIM
            + f"✅ Task tool initialized with dynamic description ({len(description)} characters)"
        )

    except Exception as e:
        print(Fore.YELLOW + f"⚠️  Warning: Failed to initialize agents system: {e}")
        print(Fore.YELLOW + "🔄 Falling back to basic Task tool functionality")


# Initialize the agents system
initialize_agents_system()


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
    from coding_agent.utils.banner import show_startup_screen
    from coding_agent.core.agent_registry import AgentRegistry
    
    # Get agent information for startup screen
    try:
        registry = AgentRegistry()
        agent_count = registry.get_agent_count()
    except:
        agent_count = None
    
    # Get working directory
    current_dir = os.getcwd()
    
    # Show beautiful startup screen
    show_startup_screen(agent_count=agent_count, working_dir=current_dir)

    # Check for LLM provider from command line
    llm_provider = os.getenv('SONPH_LLM_PROVIDER')
    agent = CodingAgent(provider_name=llm_provider)
    
    # Show quick command reference
    print(Fore.YELLOW + Style.BRIGHT + "Quick Commands:")
    print(Fore.CYAN + "  quit/exit" + Fore.WHITE + " - Exit the program")
    print(Fore.CYAN + "  reset" + Fore.WHITE + " - Clear conversation history")  
    print(Fore.CYAN + "  cd <dir>" + Fore.WHITE + " - Change working directory")
    print(Fore.CYAN + "  /init" + Fore.WHITE + " - Analyze codebase and create CLAUDE.md")
    print(Fore.CYAN + "  /commands" + Fore.WHITE + " - List all available commands")
    print(Fore.CYAN + "  /memory" + Fore.WHITE + " - View current memory context")
    print(Fore.CYAN + "  /model" + Fore.WHITE + " - Switch LLM provider (claude/deepseek)")
    print()
    print(Fore.YELLOW + "💡 Press Ctrl+C to cancel any long-running operation")
    print(Fore.BLACK + Style.BRIGHT + "─" * 80)
    print()
    
    # Set working directory if provided via environment
    initial_dir = os.getenv('INITIAL_DIR')
    if initial_dir and os.path.isdir(initial_dir):
        agent.set_working_dir(initial_dir)

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

        # Handle native and custom commands
        if user_input.strip().startswith("/"):
            parts = user_input.strip()[1:].split(" ", 1)
            command_name = parts[0]
            arguments = parts[1] if len(parts) > 1 else ""

            # Check if this is a native command first
            if agent.native_command_manager.is_native_command(command_name):
                print(Fore.CYAN + f"\n🔧 Executing native command: /{command_name}")

                try:
                    processed_message = (
                        agent.native_command_manager.process_native_command(
                            command_name, arguments
                        )
                    )
                    response = agent.chat(processed_message)
                    print(Fore.GREEN + f"\n🤖 Agent: {response}")
                except Exception as e:
                    print(Fore.RED + f"❌ Error executing /{command_name}: {str(e)}")
                continue

            # Check for special commands that aren't in the native command system yet
            elif command_name == "commands":
                print(Fore.CYAN + "\n📋 Available Commands:")
                print(Fore.CYAN + "=" * 40)

                # Show native commands
                native_commands = agent.native_command_manager.list_native_commands()
                if native_commands:
                    print(Fore.YELLOW + "Native Commands:")
                    for cmd in sorted(native_commands):
                        print(Fore.WHITE + f"  /{cmd}")

                # Show custom commands
                custom_commands = agent.command_manager.list_commands()
                if custom_commands:
                    print(Fore.YELLOW + "Custom Commands:")
                    for cmd in sorted(custom_commands):
                        print(Fore.WHITE + f"  /{cmd}")
                    print(
                        Fore.YELLOW + f"\nFound {len(custom_commands)} custom commands"
                    )
                    print(Fore.YELLOW + "Usage: /<command_name> [arguments]")
                else:
                    print(
                        Fore.YELLOW + "No custom commands found in ~/.claude/commands/"
                    )
                print(Fore.CYAN + "=" * 40)
                continue

            elif command_name == "memory":
                print(Fore.CYAN + "\n🧠 Current Memory Context:")
                print(Fore.CYAN + "=" * 50)
                if hasattr(agent, "memory_context") and agent.memory_context:
                    # Show first 1000 chars to avoid overwhelming output
                    context_preview = agent.memory_context[:1000]
                    if len(agent.memory_context) > 1000:
                        context_preview += f"\n\n... (truncated, total length: {len(agent.memory_context)} chars)"
                    print(Fore.WHITE + context_preview)
                else:
                    print(Fore.YELLOW + "No memory context loaded.")
                print(Fore.CYAN + "=" * 50)
                continue

            elif command_name == "model":
                from coding_agent.core.llm_providers import LLMProviderFactory
                
                if not arguments:
                    # Show current model and available providers
                    print(Fore.CYAN + "\n🤖 Current Model:")
                    print(Fore.GREEN + f"   {agent.get_current_provider_info()}")
                    print(Fore.CYAN + "\n📋 Available Providers:")
                    providers = LLMProviderFactory.get_available_providers()
                    for provider in providers:
                        print(Fore.WHITE + f"   {provider}")
                    print(Fore.CYAN + "\nUsage: /model <provider> [model_name]")
                    print(Fore.YELLOW + "Examples:")
                    print(Fore.WHITE + "   /model claude")
                    print(Fore.WHITE + "   /model deepseek")
                    print(Fore.WHITE + "   /model sonnet claude-sonnet-4-20250514")
                    continue
                
                # Parse arguments
                parts = arguments.split()
                provider_name = parts[0]
                model_name = parts[1] if len(parts) > 1 else None
                
                # Switch provider
                print(Fore.CYAN + f"\n🔄 Switching to {provider_name}...")
                if agent.switch_provider(provider_name, model_name):
                    print(Fore.GREEN + f"✅ Now using: {agent.get_current_provider_info()}")
                continue

            # Check if this is a custom command
            command = agent.command_manager.get_command(command_name)
            if command:
                print(Fore.CYAN + f"\n🔧 Executing custom command: /{command_name}")

                # Process the command
                processed_message = command.process(arguments)

                try:
                    response = agent.chat(processed_message)
                    print(Fore.GREEN + f"\n🤖 Agent: {response}")
                except Exception as e:
                    print(Fore.RED + f"❌ Error executing /{command_name}: {str(e)}")
                continue
            else:
                print(Fore.RED + f"❌ Unknown command: /{command_name}")
                print(Fore.YELLOW + "Use '/commands' to see available commands")
                continue

        try:
            response = agent.chat(user_input)
            print(Fore.GREEN + f"\n🤖 Agent: {response}")
        except Exception as e:
            print(Fore.RED + f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    interactive()
