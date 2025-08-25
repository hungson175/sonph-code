"""Background shell process management."""


class BackgroundShellManager:
    """Manages background shell processes and cancellation."""

    def __init__(self):
        self.background_shells = {}
        self.current_process = None
        self.cancellation_requested = False

    def reset_cancellation(self):
        """Reset the cancellation flag."""
        self.cancellation_requested = False

    def request_cancellation(self):
        """Request cancellation and terminate current process if any."""
        self.cancellation_requested = True
        if self.current_process:
            try:
                self.current_process.terminate()
            except Exception:
                pass

    def add_shell(self, shell_id: str, shell_info: dict):
        """Add a new background shell."""
        self.background_shells[shell_id] = shell_info

    def get_shell(self, shell_id: str):
        """Get shell info by ID."""
        return self.background_shells.get(shell_id)

    def list_shells(self):
        """List all shell IDs."""
        return list(self.background_shells.keys())


# Global shell manager instance
shell_manager = BackgroundShellManager()
