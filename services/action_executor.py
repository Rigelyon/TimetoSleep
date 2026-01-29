import process_manager


class ActionExecutor:
    @staticmethod
    def execute(action, selected_processes=None):
        """
        Executes the specified action.

        Args:
            action (str): The action to perform ("Terminate Process", "Shutdown", etc.).
            selected_processes (list): List of process dicts to terminate (only for "Terminate Process").

        Returns:
            dict: A result dictionary with keys 'success', 'message', 'count' (optional).
        """
        if action == "Terminate Process":
            if not selected_processes:
                return {"success": False, "message": "No processes selected."}

            success_count = 0
            for proc in selected_processes:
                # Assuming proc has 'pids' key as per existing logic
                if process_manager.kill_processes(proc.get("pids", [])):
                    success_count += 1

            return {
                "success": True,
                "count": success_count,
                "total": len(selected_processes),
                "type": "termination",
            }

        elif action == "Shutdown":
            process_manager.shutdown_system()
            return {
                "success": True,
                "message": "Shutting down system...",
                "type": "system",
            }

        elif action == "Restart":
            process_manager.restart_system()
            return {
                "success": True,
                "message": "Restarting system...",
                "type": "system",
            }

        elif action == "Lock":
            process_manager.lock_system()
            return {
                "success": True,
                "message": "Locking workstation...",
                "type": "system",
            }

        elif action == "Sleep":
            process_manager.sleep_system()
            return {
                "success": True,
                "message": "Putting system to sleep...",
                "type": "system",
            }

        return {"success": False, "message": f"Unknown action: {action}"}
