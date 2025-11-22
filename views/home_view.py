import flet as ft
import process_manager
import threading
import time
from datetime import datetime, timedelta
from state import app_state


class HomeView(ft.Column):
    def __init__(self):
        super().__init__()
        self.visible = True
        self.expand = True
        self.scroll = "auto"
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        # State
        self.selected_processes = []
        self.timer_running = False
        self.remaining_seconds = 0
        self.timer_thread = None
        self.all_processes = []

        # UI Components
        self.header = ft.Text(
            "Time to Sleep", size=30, weight=ft.FontWeight.BOLD, color="blue400"
        )
        self.sub_header = ft.Text("Auto-terminate apps", size=14, color="grey400")

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

        self.selected_process_text = ft.Text(
            "No process selected", italic=True, color="grey500"
        )

        # Timer Type Selector
        self.timer_type_dropdown = ft.Dropdown(
            label="Timer Type",
            options=[
                ft.dropdown.Option("Countdown"),
                ft.dropdown.Option("Specific Time"),
            ],
            value="Countdown",
            on_change=self.on_timer_type_change,
            expand=True,
        )

        # Action Selector
        self.action_dropdown = ft.Dropdown(
            label="Action",
            options=[
                ft.dropdown.Option("Terminate Process"),
            ],
            value="Terminate Process",
            expand=True,
        )

        # Timer Inputs (Countdown)
        self.hours_input = ft.TextField(
            label="Hours",
            value="0",
            width=80,
            text_align=ft.TextAlign.CENTER,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        self.minutes_input = ft.TextField(
            label="Mins",
            value="0",
            width=80,
            text_align=ft.TextAlign.CENTER,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        self.seconds_input = ft.TextField(
            label="Secs",
            value="0",
            width=80,
            text_align=ft.TextAlign.CENTER,
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        self.countdown_inputs = ft.Row(
            [self.hours_input, self.minutes_input, self.seconds_input],
            alignment=ft.MainAxisAlignment.CENTER,
        )

        # Specific Time Inputs
        self.selected_time = None
        self.time_picker = ft.TimePicker(
            confirm_text="Confirm",
            error_invalid_text="Time invalid",
            help_text="Pick your time",
            on_change=self.on_time_picked,
        )

        self.time_input_field = ft.TextField(
            value="Tap to select time",
            read_only=True,
            width=200,
            text_align=ft.TextAlign.CENTER,
            prefix_icon="access_time",
            on_click=lambda _: app_state.page.open(self.time_picker),
        )

        self.day_status_text = ft.Text(
            "Today", size=16, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER
        )
        self.date_display_text = ft.Text(
            value=datetime.now().strftime("%A, %d %B %Y"),
            size=12,
            color="grey400",
            text_align=ft.TextAlign.CENTER,
        )

        self.specific_time_inputs = ft.Row(
            [
                ft.Column(
                    [
                        ft.Text(
                            "Target Time:",
                            size=12,
                            color="grey500",
                            text_align=ft.TextAlign.CENTER,
                        ),
                        self.time_input_field,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True,
                ),
                ft.Container(width=20),  # Spacer
                ft.Column(
                    [
                        ft.Text(
                            "Target Date:",
                            size=12,
                            color="grey500",
                            text_align=ft.TextAlign.CENTER,
                        ),
                        self.day_status_text,
                        self.date_display_text,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            visible=False,
        )

        # Progress Ring
        self.progress_ring = ft.ProgressRing(
            width=200, height=200, stroke_width=15, value=0, color="blue500"
        )
        self.countdown_text = ft.Text("00:00:00", size=40, weight=ft.FontWeight.BOLD)

        # Containers
        self.timer_container = ft.Column(
            [
                ft.Stack(
                    [
                        self.progress_ring,
                        ft.Container(
                            content=self.countdown_text,
                            alignment=ft.alignment.center,
                            width=200,
                            height=200,
                        ),
                    ]
                ),
                ft.Text("Target:", color="grey400"),
                self.selected_process_text,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            visible=False,
        )

        self.setup_container = ft.Column(
            [
                ft.Text("Configuration:", weight=ft.FontWeight.BOLD),
                ft.Row(
                    [
                        self.timer_type_dropdown,
                        ft.Container(width=20),
                        self.action_dropdown,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Divider(),
                ft.Text("Select a process to terminate:", weight=ft.FontWeight.BOLD),
                ft.Row([self.search_field, self.refresh_button]),
                ft.Container(
                    content=self.process_list_view,
                    height=250,
                    border=ft.border.all(1, "grey800"),
                    border_radius=10,
                    padding=5,
                ),
                ft.Divider(),
                ft.Text("Timer Settings:", weight=ft.FontWeight.BOLD),
                self.countdown_inputs,
                self.specific_time_inputs,
            ]
        )

        # Buttons
        self.start_button = ft.ElevatedButton(
            "Start Timer",
            icon="play_arrow",
            style=ft.ButtonStyle(
                color="white",
                bgcolor="blue600",
                padding=20,
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
            on_click=self.start_timer,
            width=200,
        )

        self.cancel_button = ft.ElevatedButton(
            "Cancel",
            icon="stop",
            style=ft.ButtonStyle(
                color="white",
                bgcolor="red600",
                padding=20,
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
            on_click=self.cancel_timer,
            width=200,
            visible=False,
        )

        self.controls_list = [
            self.header,
            self.sub_header,
            ft.Divider(height=20, color="transparent"),
            self.setup_container,
            self.timer_container,
            ft.Divider(height=20, color="transparent"),
            ft.Row(
                [self.start_button, self.cancel_button],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ]

        self.controls = [
            ft.Container(
                padding=20,
                content=ft.Column(
                    self.controls_list,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            )
        ]

        # Register callback
        app_state.refresh_processes_callback = self.refresh_processes
        self.refresh_processes()

    def on_timer_type_change(self, e):
        is_countdown = self.timer_type_dropdown.value == "Countdown"
        self.countdown_inputs.visible = is_countdown
        self.specific_time_inputs.visible = not is_countdown
        app_state.page.update()

    def on_time_picked(self, e):
        self.selected_time = self.time_picker.value
        if self.selected_time:
            self.time_input_field.value = self.selected_time.strftime("%H:%M")

            # Update date display
            now = datetime.now()
            target_dt = datetime.combine(now.date(), self.selected_time)
            is_tomorrow = False
            if target_dt <= now:
                target_dt += timedelta(days=1)
                is_tomorrow = True

            self.day_status_text.value = "Tomorrow" if is_tomorrow else "Today"
            self.date_display_text.value = target_dt.strftime("%A, %d %B %Y")

        app_state.page.update()

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
                    leading_control = ft.Image(
                        src_base64=proc["icon"], width=32, height=32
                    )
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

        if app_state.page:
            app_state.page.update()

    def select_process(self, proc):
        # Check if already selected (by name)
        existing = next(
            (p for p in self.selected_processes if p["name"] == proc["name"]), None
        )

        if existing:
            self.selected_processes.remove(existing)
        else:
            self.selected_processes.append(proc)

        # Update text
        if not self.selected_processes:
            self.selected_process_text.value = "No process selected"
            self.selected_process_text.italic = True
            self.selected_process_text.color = "grey500"
        else:
            names = [p["name"] for p in self.selected_processes]
            if len(names) > 3:
                display_text = f"{len(names)} apps selected"
            else:
                display_text = ", ".join(names)
            self.selected_process_text.value = display_text
            self.selected_process_text.italic = False
            self.selected_process_text.color = "white"

        # Update visual selection
        selected_names = [p["name"] for p in self.selected_processes]
        for tile in self.process_list_view.controls:
            if tile.data in selected_names:
                tile.bgcolor = "blue900"
            else:
                tile.bgcolor = None

        if app_state.page:
            app_state.page.update()

    def start_timer(self, e):
        if not self.selected_processes:
            app_state.page.open(
                ft.SnackBar(content=ft.Text("Please select at least one process!"))
            )
            return

        total_seconds = 0

        if self.timer_type_dropdown.value == "Countdown":
            try:
                h = int(self.hours_input.value)
                m = int(self.minutes_input.value)
                s = int(self.seconds_input.value)
                total_seconds = h * 3600 + m * 60 + s
            except ValueError:
                app_state.page.open(ft.SnackBar(content=ft.Text("Invalid time input!")))
                return
        else:  # Specific Time
            if not self.selected_time:
                app_state.page.open(ft.SnackBar(content=ft.Text("Please pick a time!")))
                return

            now = datetime.now()
            target_time = datetime.combine(now.date(), self.selected_time)

            if target_time <= now:
                # If time has passed today, assume tomorrow
                target_time += timedelta(days=1)

            diff = target_time - now
            total_seconds = int(diff.total_seconds())

        if total_seconds <= 0:
            app_state.page.open(
                ft.SnackBar(content=ft.Text("Time must be greater than 0!"))
            )
            return

        # Switch UI
        self.setup_container.visible = False
        self.timer_container.visible = True
        self.start_button.visible = False
        self.cancel_button.visible = True

        self.timer_running = True
        self.remaining_seconds = total_seconds

        self.timer_thread = threading.Thread(
            target=self.run_timer, args=(total_seconds,), daemon=True
        )
        self.timer_thread.start()
        app_state.page.update()

    def run_timer(self, total_seconds):
        while self.remaining_seconds > 0 and self.timer_running:
            mins, secs = divmod(self.remaining_seconds, 60)
            hours, mins = divmod(mins, 60)

            self.countdown_text.value = "{:02d}:{:02d}:{:02d}".format(hours, mins, secs)
            self.progress_ring.value = self.remaining_seconds / total_seconds

            app_state.page.update()
            time.sleep(1)
            self.remaining_seconds -= 1

        if self.timer_running:  # If not cancelled
            # Timer finished
            self.countdown_text.value = "00:00:00"
            self.progress_ring.value = 0
            app_state.page.update()

            self.execute_action()

            self.reset_ui()

    def execute_action(self):
        action = self.action_dropdown.value

        if action == "Terminate Process":
            success_count = 0
            for proc in self.selected_processes:
                if process_manager.kill_processes(proc["pids"]):
                    success_count += 1

            if success_count == len(self.selected_processes):
                app_state.page.open(
                    ft.SnackBar(
                        content=ft.Text(
                            f"Successfully terminated {success_count} apps!"
                        ),
                        bgcolor="green700",
                    )
                )
            elif success_count > 0:
                app_state.page.open(
                    ft.SnackBar(
                        content=ft.Text(
                            f"Terminated {success_count}/{len(self.selected_processes)} apps."
                        ),
                        bgcolor="orange700",
                    )
                )
            else:
                app_state.page.open(
                    ft.SnackBar(
                        content=ft.Text("Failed to terminate selected apps."),
                        bgcolor="red700",
                    )
                )

    def cancel_timer(self, e):
        self.timer_running = False
        self.reset_ui()
        app_state.page.open(ft.SnackBar(content=ft.Text("Timer cancelled.")))

    def reset_ui(self):
        self.setup_container.visible = True
        self.timer_container.visible = False
        self.start_button.visible = True
        self.cancel_button.visible = False
        app_state.page.update()
