import flet as ft
from state import app_state
import process_manager


class ProcessSelector(ft.Column):
    def __init__(self, on_selection_change=None):
        super().__init__()
        self.on_selection_change = on_selection_change
        self.selected_processes = []
        self.all_processes = []

        self.search_field = ft.TextField(
            hint_text="Search process...",
            prefix_icon="search",
            border_radius=10,
            on_change=lambda e: self.filter_processes(e.control.value),
            expand=True,
        )

        self.refresh_button = ft.IconButton(
            icon="refresh",
            tooltip="Refresh Process List",
            on_click=lambda e: self.refresh_processes(),
        )

        self.process_list_view = ft.ListView(expand=True, spacing=10, padding=10)

        self.controls = [
            ft.Text(
                "Select a Process to Terminate:", weight=ft.FontWeight.BOLD, size=16
            ),
            ft.Container(height=5),
            ft.Row([self.search_field, self.refresh_button]),
            ft.Container(
                content=self.process_list_view,
                height=250,
                border=ft.border.all(1, "grey800"),
                border_radius=10,
                padding=5,
            ),
            ft.Container(height=5),
        ]

        # Register callback
        app_state.refresh_processes_callback = self.refresh_processes

    def refresh_processes(self):
        self.all_processes = process_manager.get_running_processes(
            show_all=app_state.show_system_processes
        )
        self.filter_processes(
            self.search_field.value if self.search_field.value else ""
        )

    def filter_processes(self, query):
        self.process_list_view.controls.clear()
        query = query.lower()
        selected_names = [p["name"] for p in self.selected_processes]

        for proc in self.all_processes:
            if query in proc["name"].lower():
                # Determine icon
                if proc.get("icon"):
                    leading_control = ft.Image(src="", width=32, height=32)
                    leading_control.src_base64 = proc["icon"]
                else:
                    leading_control = ft.Icon("apps")

                # Create a list tile for each process
                tile = ft.ListTile(
                    leading=leading_control,
                    title=ft.Text(proc["name"]),
                    subtitle=ft.Text(f"{len(proc['pids'])} processes"),
                    on_click=lambda e, p=proc: self.select_process(p),
                    hover_color="grey900",
                    data=proc["name"],
                )

                if proc["name"] in selected_names:
                    tile.bgcolor = "blue900"

                self.process_list_view.controls.append(tile)

        self.update()

    def select_process(self, proc):
        # Check if already selected (by name)
        existing = next(
            (p for p in self.selected_processes if p["name"] == proc["name"]), None
        )

        if existing:
            self.selected_processes.remove(existing)
        else:
            self.selected_processes.append(proc)

        # Update visual selection
        selected_names = [p["name"] for p in self.selected_processes]
        for tile in self.process_list_view.controls:
            if tile.data in selected_names:
                tile.bgcolor = "blue900"
            else:
                tile.bgcolor = None

        self.update()

        if self.on_selection_change:
            self.on_selection_change(self.selected_processes)
