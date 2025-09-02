"""Keyboard interrupt and monitoring utilities."""

import signal
import threading

from colorama import Fore

from ..core.config import Config
from ..core.shell_manager import shell_manager


def setup_keyboard_interrupt():
    """Setup keyboard interrupt handling for Esc key"""

    def signal_handler(*_):
        shell_manager.request_cancellation()
        print(f"\n{Fore.YELLOW}⚠️  Process cancelled by user (Ctrl+C pressed)")
        raise KeyboardInterrupt("User pressed Ctrl+C")

    signal.signal(signal.SIGINT, signal_handler)


def start_keyboard_monitor():
    """Start monitoring for Esc key in a separate thread"""

    def monitor_keyboard():
        try:
            import sys
            import select
            import tty
            import termios

            if sys.stdin.isatty():
                old_settings = termios.tcgetattr(sys.stdin)
                tty.setraw(sys.stdin.fileno())

                while not shell_manager.cancellation_requested:
                    if select.select(
                        [sys.stdin], [], [], Config.KEYBOARD_POLL_INTERVAL
                    )[0]:
                        key = sys.stdin.read(1)
                        if ord(key) == Config.ESC_KEY_CODE:  # Esc key
                            if shell_manager.current_process:
                                shell_manager.current_process.terminate()
                                print(
                                    f"\n{Fore.YELLOW}⚠️  Tool execution cancelled (Esc pressed)"
                                )
                                break

                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        except Exception:
            pass  # Fallback gracefully if terminal handling fails

    thread = threading.Thread(target=monitor_keyboard, daemon=True)
    thread.start()
    return thread
