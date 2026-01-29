import flet as ft
import process_manager
import threading
import time
from datetime import datetime, timedelta
from state import app_state
from views.components.timer_control import TimerControl
from views.components.process_selector import ProcessSelector
from views.components.timer_setup import TimerSetup


class HomeView(ft.Column):
    def __init__(self):
        super().__init__()
        self.visible = True
        self.expand = True
        self.scroll = "auto"
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        # State
        self.timer_running = False
        self.remaining_seconds = 0
        self.timer_thread = None

        # UI Components
        self.header = ft.Text(
            "Time to Sleep", size=30, weight=ft.FontWeight.BOLD, color="blue400"
        )
        self.sub_header = ft.Text("Auto-terminate apps", size=14, color="grey400")

        # Modularized Components
        self.timer_control = TimerControl()
        self.process_selector = ProcessSelector(
            on_selection_change=self.on_process_selection_change
        )
        self.timer_setup = TimerSetup(on_action_change=self.on_action_change)

        self.selected_process_text = ft.Text(
            "No process selected", italic=True, color="grey500"
        )

        self.action_description_text = ft.Text(
            "System will shutdown when timer ends.",
            size=16,
            weight=ft.FontWeight.BOLD,
            color="orange400",
            visible=False,
            text_align=ft.TextAlign.CENTER,
        )

        # Finish time info components
        self.finish_day_text = ft.Text("", size=16, weight=ft.FontWeight.BOLD)
        self.finish_date_text = ft.Text("", size=12, color="grey400")
        self.finish_clock_text = ft.Text(
            "", size=16, weight=ft.FontWeight.BOLD, color="blue400"
        )

        # Containers
        self.timer_container = ft.Column(
            [
                self.timer_control,
                ft.Container(height=10),
                ft.Text("Target:", color="grey400"),
                self.selected_process_text,
                ft.Container(height=10),
                self.finish_day_text,
                self.finish_date_text,
                self.finish_clock_text,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            visible=False,
        )

        self.setup_container = ft.Column(
            [
                self.timer_setup,
                ft.Divider(),
                self.process_selector,
            ]
        )

        self.divider = ft.Divider()
        self.timer_setup.controls.insert(2, self.divider)
        self.timer_setup.controls.insert(3, self.process_selector)
        self.timer_setup.controls.insert(4, self.action_description_text)

        self.setup_container = self.timer_setup  # Use TimerSetup as the main container

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

    def did_mount(self):
        # Initial refresh
        self.process_selector.refresh_processes()

    def on_process_selection_change(self, selected_processes):
        if not selected_processes:
            self.selected_process_text.value = "No process selected"
            self.selected_process_text.italic = True
            self.selected_process_text.color = "grey500"
        else:
            names = [p["name"] for p in selected_processes]
            if len(names) > 3:
                display_text = f"{len(names)} apps selected"
            else:
                display_text = ", ".join(names)
            self.selected_process_text.value = display_text
            self.selected_process_text.italic = False
            self.selected_process_text.color = "white"
        self.update()

    def on_action_change(self, action):
        is_terminate = action == "Terminate Process"
        self.process_selector.visible = is_terminate
        self.divider.visible = is_terminate  # Assuming I made it an instance attribute
        self.action_description_text.visible = not is_terminate

        if not is_terminate:
            self.action_description_text.value = (
                f"System will {action.lower()} when timer ends."
            )
            self.selected_process_text.value = f"Action: {action}"
            self.selected_process_text.italic = False
            self.selected_process_text.color = "white"

        # Trigger update of process selector text if we switched back to terminate
        if is_terminate:
            self.on_process_selection_change(self.process_selector.selected_processes)

        self.update()

    def start_timer(self, e):
        action = self.timer_setup.action_dropdown.value
        if (
            action == "Terminate Process"
            and not self.process_selector.selected_processes
        ):
            app_state.page.open(
                ft.SnackBar(content=ft.Text("Please select at least one process!"))
            )
            return

        total_seconds = self.timer_setup.get_total_seconds()

        if total_seconds == -1:
            app_state.page.open(ft.SnackBar(content=ft.Text("Invalid time input!")))
            return
        elif total_seconds == -2:
            app_state.page.open(ft.SnackBar(content=ft.Text("Please pick a time!")))
            return

        if total_seconds <= 0:
            app_state.page.open(
                ft.SnackBar(content=ft.Text("Time must be greater than 0!"))
            )
            return

        # Check if duration exceeds 999 hours
        if total_seconds >= 1000 * 3600:
            app_state.page.open(
                ft.SnackBar(content=ft.Text("Timer cannot exceed 999 hours!"))
            )
            return

        # Switch UI
        self.setup_container.visible = False
        self.timer_container.visible = True
        self.start_button.visible = False
        self.cancel_button.visible = True

        self.timer_running = True
        self.remaining_seconds = total_seconds

        # Calculate finish time info
        now = datetime.now()
        finish_time = now + timedelta(seconds=total_seconds)

        diff_days = (finish_time.date() - now.date()).days
        if diff_days == 0:
            relative_day = "Today"
        elif diff_days == 1:
            relative_day = "Tomorrow"
        else:
            relative_day = f"In {diff_days} days"

        full_date = finish_time.strftime("%A, %d %B %Y")
        finish_time_str = finish_time.strftime("%H:%M")

        self.finish_day_text.value = relative_day
        self.finish_date_text.value = full_date
        self.finish_clock_text.value = finish_time_str

        self.timer_thread = threading.Thread(
            target=self.run_timer, args=(total_seconds,), daemon=True
        )
        self.timer_thread.start()
        self.update()

    def run_timer(self, total_seconds):
        while self.remaining_seconds > 0 and self.timer_running:
            self.timer_control.update_timer(self.remaining_seconds, total_seconds)
            time.sleep(1)
            self.remaining_seconds -= 1

        if self.timer_running:  # If not cancelled
            # Timer finished
            self.timer_control.update_timer(0, total_seconds)
            self.execute_action()
            self.reset_ui()

    def execute_action(self):
        action = self.timer_setup.action_dropdown.value

        if action == "Terminate Process":
            success_count = 0
            for proc in self.process_selector.selected_processes:
                if process_manager.kill_processes(proc["pids"]):
                    success_count += 1

            if success_count == len(self.process_selector.selected_processes):
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
                            f"Terminated {success_count}/{len(self.process_selector.selected_processes)} apps."
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
        elif action == "Shutdown":
            process_manager.shutdown_system()
            app_state.page.open(ft.SnackBar(content=ft.Text("Shutting down...")))
        elif action == "Restart":
            process_manager.restart_system()
            app_state.page.open(ft.SnackBar(content=ft.Text("Restarting...")))
        elif action == "Lock":
            process_manager.lock_system()
            app_state.page.open(ft.SnackBar(content=ft.Text("Locking workstation...")))
        elif action == "Sleep":
            process_manager.sleep_system()
            app_state.page.open(ft.SnackBar(content=ft.Text("Going to sleep...")))

    def cancel_timer(self, e):
        self.timer_running = False
        self.reset_ui()
        app_state.page.open(ft.SnackBar(content=ft.Text("Timer cancelled.")))

    def reset_ui(self):
        self.setup_container.visible = True
        self.timer_container.visible = False
        self.start_button.visible = True
        self.cancel_button.visible = False
        self.timer_control.reset()
        self.update()
