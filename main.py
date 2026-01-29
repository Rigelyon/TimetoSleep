import flet as ft
from views.home_view import HomeView
from views.settings_view import SettingsView
from state import app_state
from services.timer_service import TimerService
from services.tray_service import TrayService
import threading
import time


def main(page: ft.Page):
    app_state.set_page(page)

    page.title = "Time to Sleep"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.window.width = 500
    page.window.height = 750
    page.window.resizable = True
    page.update()

    # Initialize Services
    if not app_state.timer_service:
        app_state.timer_service = TimerService()

    tray_service = TrayService()
    tray_service.run_detached()

    # Window Event Handler (Minimize Polling because event is unreliable)
    def minimize_watcher():
        while True:
            try:
                if page.window.minimized and app_state.minimize_to_tray:
                    # Only hide logic if tray is actually running
                    if tray_service.is_active():
                        page.window.visible = False
                        page.update()
                    # If tray failed, standard minimize happens (window stays in taskbar, just minimized)
            except Exception:
                pass
            time.sleep(0.3)

    threading.Thread(target=minimize_watcher, daemon=True).start()

    # Views
    home_view = HomeView()
    settings_view = SettingsView()

    def on_nav_change(e):
        index = e.control.selected_index
        home_view.visible = index == 0
        settings_view.visible = index == 1
        page.update()

    page.navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon="home", label="Home"),
            ft.NavigationBarDestination(icon="settings", label="Settings"),
        ],
        on_change=on_nav_change,
    )

    # Layout Assembly
    page.add(ft.Column([home_view, settings_view], expand=True))


if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")
