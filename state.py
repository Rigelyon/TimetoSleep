import flet as ft


class AppState:
    def __init__(self):
        self.page: ft.Page = None
        self.show_system_processes = False
        self.refresh_processes_callback = None

    def set_page(self, page: ft.Page):
        self.page = page

    def toggle_system_processes(self, value):
        self.show_system_processes = value
        if self.refresh_processes_callback:
            self.refresh_processes_callback()


app_state = AppState()
