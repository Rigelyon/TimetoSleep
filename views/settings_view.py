import flet as ft
from state import app_state


class SettingsView(ft.Column):
    def __init__(self):
        super().__init__()
        self.visible = False
        self.controls = [
            ft.Container(
                padding=20,
                content=ft.Column(
                    [
                        ft.Text("Settings", size=30, weight=ft.FontWeight.BOLD),
                        ft.Divider(),
                        ft.Switch(
                            label="Dark Mode", value=True, on_change=self.toggle_theme
                        ),
                        ft.Switch(
                            label="Show System Processes",
                            value=app_state.show_system_processes,
                            on_change=self.toggle_system_processes,
                        ),
                        ft.Switch(
                            label="Minimize to Tray",
                            value=app_state.minimize_to_tray,
                            on_change=self.toggle_minimize_to_tray,
                        ),
                        ft.Divider(),
                        ft.Text("About", size=20, weight=ft.FontWeight.BOLD),
                        ft.Text("Time to Sleep v1.0", color="grey500"),
                        ft.Text("Created with Flet & Python", color="grey500"),
                    ]
                ),
            )
        ]

    def toggle_theme(self, e):
        if app_state.page:
            app_state.page.theme_mode = (
                ft.ThemeMode.LIGHT
                if app_state.page.theme_mode == ft.ThemeMode.DARK
                else ft.ThemeMode.DARK
            )
            app_state.page.update()

    def toggle_system_processes(self, e):
        app_state.toggle_system_processes(e.control.value)

    def toggle_minimize_to_tray(self, e):
        app_state.minimize_to_tray = e.control.value
