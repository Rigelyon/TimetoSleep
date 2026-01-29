import pystray
from PIL import Image
import threading
from state import app_state
import os


class TrayService:
    def __init__(self, icon_path="assets/icon.ico"):
        self.icon_path = icon_path
        self.icon = None
        self._thread = None
        # Bind handlers
        self.on_open_handler = self._default_on_open
        self.on_exit_handler = self._default_on_exit
        self._enable_dpi_awareness()
        self._enable_dark_mode()

    def _enable_dpi_awareness(self):
        try:
            import ctypes

            # Try SetProcessDpiAwareness (Windows 8.1+)
            # 0 = Unaware, 1 = System DPI Aware, 2 = Per Monitor DPI Aware
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            try:
                # Fallback to SetProcessDPIAware (Windows Vista+)
                import ctypes

                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass
        self._enable_dark_mode()

    def _enable_dark_mode(self):
        try:
            import ctypes

            # Attempt to enable dark mode for the app/tray menu
            # Ordinal 135 is SetPreferredAppMode (Windows 10 1903+)
            # 0 = Default, 1 = AllowDark, 2 = ForceDark
            ctypes.windll.uxtheme[135](2)
        except Exception:
            pass

    def setup(self):
        if not os.path.exists(self.icon_path):
            print(f"Warning: Icon file not found at {self.icon_path}")
            return

        try:
            image = Image.open(self.icon_path)

            # Define menu
            menu = pystray.Menu(
                pystray.MenuItem("Open", self.on_open_click, default=True),
                pystray.MenuItem(
                    "Pause/Resume", self.on_pause_click, checked=self.is_paused_checked
                ),
                pystray.MenuItem("Cancel", self.on_cancel_click),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Exit", self.on_exit_click),
            )

            self.icon = pystray.Icon("TimeToSleep", image, "Time to Sleep", menu)
        except Exception as e:
            print(f"Failed to setup tray icon: {e}")

    def run_detached(self):
        if not self.icon:
            self.setup()

        if self.icon:
            self._thread = threading.Thread(target=self.icon.run, daemon=True)
            self._thread.start()

            # Register listener to timer service if available
            # Note: TimerService might be recreated or we rely on app_state.timer_service
            # ideally timer_service is singleton in app_state.

            # We can start a loop to update tooltip if needed, or register listener
            # For now, let's just allow the menu actions to work.
            # To update tooltip with progress, we need to register a listener.
            if app_state.timer_service:
                app_state.timer_service.add_tick_listener(self.update_tooltip)
                app_state.timer_service.add_finish_listener(self.on_timer_finish)
                app_state.timer_service.add_pause_listener(self.on_pause_change)

    def on_pause_change(self, is_paused):
        if self.icon:
            # This triggers re-evaluation of menu items (checked state)
            self.icon.update_menu()

    def update_tooltip(self, remaining, total):
        if self.icon:
            percent = int((remaining / total) * 100) if total > 0 else 0
            time_str = self.format_time(remaining)

            # Construct detailed tooltip
            status = app_state.timer_config.get("status", "Running")
            action = app_state.timer_config.get("action", "")
            target = app_state.timer_config.get("target", "")

            tooltip = f"Percentage: {percent}%\nTime Left: {time_str}\nStatus: {status}\nAction: {action}"
            if target and target != "System":
                tooltip += f" ({target})"

            self.icon.title = tooltip

    def on_timer_finish(self):
        if self.icon:
            self.icon.title = "Time to Sleep - Finished"
            self.show_notification("Timer Finished", "Your timer has finished.")

    def format_time(self, seconds):
        mins, secs = divmod(seconds, 60)
        hours, mins = divmod(mins, 60)
        if hours > 0:
            return f"{hours}:{mins:02}:{secs:02}"
        return f"{mins}:{secs:02}"

    def is_paused_checked(self, item):
        return app_state.timer_service.is_paused() if app_state.timer_service else False

    def on_open_click(self, icon, item):
        if app_state.page:
            app_state.page.window.visible = True
            app_state.page.update()
            # Restore window if minimized (though we handle visibility)
            app_state.page.window.minimized = False
            app_state.page.window.center()
            app_state.page.window.to_front()  # Bring to front

    def on_pause_click(self, icon, item):
        if app_state.timer_service and app_state.timer_service.is_running():
            app_state.timer_service.toggle_pause()

    def on_cancel_click(self, icon, item):
        if app_state.timer_service and app_state.timer_service.is_running():
            app_state.timer_service.cancel_timer()
            if self.icon:
                self.icon.title = "Time to Sleep"

    def on_exit_click(self, icon, item):
        self.stop()
        if app_state.page:
            # We need to signal the app to close really.
            # Calling unique close logic.
            app_state.page.window.destroy()

    def stop(self):
        if self.icon:
            self.icon.stop()

    def show_notification(self, title, message):
        if self.icon:
            self.icon.notify(message, title)

    def _default_on_open(self):
        pass

    def _default_on_exit(self):
        pass
