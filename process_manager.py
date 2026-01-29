import psutil
import os
import icon_extractor


class IconCache:
    _cache = {}

    @classmethod
    def get_icon(cls, exe_path):
        if exe_path not in cls._cache:
            cls._cache[exe_path] = icon_extractor.get_icon_base64(exe_path)
        return cls._cache[exe_path]


def get_running_processes(show_all=False):
    """
    Retrieves a list of running processes grouped by name.
    Returns a list of dicts: {'name': str, 'pids': list[int], 'path': str, 'icon': str}
    """
    process_groups = {}
    for proc in psutil.process_iter(["pid", "name", "exe"]):
        try:
            # If show_all is False, we only show processes with an executable path (usually user apps)
            if show_all or proc.info["exe"]:
                name = proc.info["name"]
                if name not in process_groups:
                    # Try to get icon if exe exists
                    icon_b64 = None
                    exe_path = proc.info["exe"] or ""
                    if exe_path:
                        icon_b64 = IconCache.get_icon(exe_path)

                    process_groups[name] = {
                        "name": name,
                        "pids": [],
                        "path": exe_path,
                        "icon": icon_b64,
                    }
                process_groups[name]["pids"].append(proc.info["pid"])
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    # Convert to list and sort
    return sorted(process_groups.values(), key=lambda x: x["name"].lower())


def kill_processes(pids):
    """
    Terminates a list of processes by their PIDs.
    Returns True if at least one process was terminated successfully.
    """
    success_count = 0
    for pid in pids:
        try:
            process = psutil.Process(pid)
            process.terminate()
            success_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            print(f"Error killing process {pid}: {e}")

    return success_count > 0


def shutdown_system():
    os.system("shutdown /s /t 1")


def restart_system():
    os.system("shutdown /r /t 1")


def lock_system():
    import ctypes

    ctypes.windll.user32.LockWorkStation()


def sleep_system():
    # Helper to enable hibernation if needed, but for sleep we specifically want suspend
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
