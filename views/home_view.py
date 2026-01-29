import flet as ft
from datetime import datetime, timedelta
from state import app_state
from views.components.timer_control import TimerControl
from views.components.process_selector import ProcessSelector
from views.components.timer_setup import TimerSetup
from services.timer_service import TimerService
from services.action_executor import ActionExecutor


class HomeView(ft.Column):
    def __init__(self):
        super().__init__()
        self.visible = True
        self.expand = True
        self.scroll = "auto"
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        # Service
        if not app_state.timer_service:
            app_state.timer_service = TimerService()
        self.timer_service = app_state.timer_service

        # UI Components
        self.header = ft.Text(
            "Time to Sleep", size=40, weight=ft.FontWeight.BOLD, color="blue400"
        )
        self.sub_header = ft.Text(
            "It's time for you to sleep", size=16, color="grey400"
        )

        # Child Components
        self.timer_control = TimerControl()
        self.process_selector = ProcessSelector(
            on_selection_change=self.on_process_selection_change
        )
        self.timer_setup = TimerSetup(
            on_action_change=self.on_action_change,
            on_trigger_change=self.on_trigger_change,
        )

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
            # Add padding to make it look nice
        )
        # Wrap description in container for spacing
        self.action_description_container = ft.Container(
            content=self.action_description_text,
            padding=10,
            visible=False,  # Control visibility on container level if needed, or text
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

        # Layout for Setup: TimerSetup -> Process Selector / Description
        self.setup_container = ft.Column(
            [
                self.timer_setup,
                ft.Divider(),
                self.process_selector,
                self.action_description_container,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # Buttons
        self.start_button = ft.ElevatedButton(
            "Start Trigger",
            icon="play_arrow",
            style=ft.ButtonStyle(
                color="white",
                bgcolor="blue600",
                padding=20,
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
            on_click=self.on_start_click,
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
            on_click=self.on_cancel_click,
            width=200,
            visible=False,
        )

        self.pause_button = ft.ElevatedButton(
            "Pause",
            icon="pause",
            style=ft.ButtonStyle(
                color="white",
                bgcolor="orange600",
                padding=20,
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
            on_click=self.on_pause_click,
            width=200,
            visible=False,
        )

        self.controls_list = [
            self.header,
            self.sub_header,
            ft.Divider(height=20, color="transparent"),
            self.setup_container,
            self.timer_container,
            # ft.Divider(height=20, color="transparent"),
            ft.Row(
                [self.start_button, self.pause_button, self.cancel_button],
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
        # Ensure initial state is consistent
        self.current_trigger_type = self.timer_setup.trigger_type_dropdown.value
        self.on_action_change(self.timer_setup.action_dropdown.value)

        # Subscribe to pause changes
        self.timer_service.add_pause_listener(self.on_pause_change)

    def will_unmount(self):
        self.timer_service.remove_pause_listener(self.on_pause_change)

    def on_pause_change(self, is_paused):
        self.timer_control.set_paused(is_paused)
        if is_paused:
            self.pause_button.text = "Resume"
            self.pause_button.icon = "play_arrow"
            self.pause_button.style.bgcolor = "green600"
        else:
            self.pause_button.text = "Pause"
            self.pause_button.icon = "pause"
            self.pause_button.style.bgcolor = "orange600"

        # Update status in config for tray
        if app_state.timer_config:
            app_state.timer_config["status"] = "Paused" if is_paused else "Running"

        self.update()

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
        self.action_description_text.visible = not is_terminate
        self.action_description_container.visible = not is_terminate

        if not is_terminate:
            self.update_description_text(action)
            self.selected_process_text.value = f"Action: {action}"
            self.selected_process_text.italic = False
            self.selected_process_text.color = "white"

        # Trigger update of process selector text if we switched back to terminate
        if is_terminate:
            self.on_process_selection_change(self.process_selector.selected_processes)

        self.update()

    def on_trigger_change(self, trigger_type):
        self.current_trigger_type = trigger_type
        # Update description if currently showing action description
        if self.action_description_text.visible:
            current_action = self.timer_setup.action_dropdown.value
            self.update_description_text(current_action)
        self.update()

    def update_description_text(self, action):
        suffix_map = {
            "Countdown": "when timer ends.",
            "Specific Time": "at the specified time.",
            "Immediate": "immediately.",
        }
        suffix = suffix_map.get(self.current_trigger_type, "when triggered.")
        self.action_description_text.value = f"System will {action.lower()} {suffix}"

    def on_start_click(self, e):
        config = self.timer_setup.get_configuration()

        if config["error"]:
            app_state.page.open(ft.SnackBar(content=ft.Text(config["error"])))
            return

        action = config["action"]
        total_seconds = config["total_seconds"]

        # Additional validation for Process Selection
        if (
            action == "Terminate Process"
            and not self.process_selector.selected_processes
        ):
            app_state.page.open(
                ft.SnackBar(content=ft.Text("Please select at least one process!"))
            )
            return

        # Check max duration
        if total_seconds >= 1000 * 3600:
            app_state.page.open(
                ft.SnackBar(content=ft.Text("Timer cannot exceed 999 hours!"))
            )
            return

        # Immediate Execution
        if config["trigger_type"] == "Immediate":
            self.on_timer_finish()
            return

        # Switch UI
        self.setup_container.visible = False
        self.timer_container.visible = True
        self.start_button.visible = False
        self.pause_button.visible = True
        self.cancel_button.visible = True

        # Reset pause button state
        self.pause_button.text = "Pause"
        self.pause_button.icon = "pause"
        self.pause_button.style.bgcolor = "orange600"

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

        self.finish_day_text.value = relative_day
        self.finish_date_text.value = finish_time.strftime("%A, %d %B %Y")
        self.finish_clock_text.value = finish_time.strftime("%H:%M")

        # Start Service
        self.timer_service.start_timer(
            total_seconds, on_tick=self.on_timer_tick, on_finish=self.on_timer_finish
        )

        # Update AppState config for Tray
        app_state.timer_config = {
            "action": action,
            "target": self._get_target_description(),
            "status": "Running",
            "total_seconds": total_seconds,
        }
        self.update()

    def _get_target_description(self):
        config = self.timer_setup.get_configuration()
        action = config["action"]
        if action == "Terminate Process":
            count = len(self.process_selector.selected_processes)
            if count == 1:
                return self.process_selector.selected_processes[0]["name"]
            return f"{count} apps"
        return "System"

    def on_timer_tick(self, remaining, total):
        # This callback comes from a thread, so we must not update UI directly if Flet is picky,
        # but Flet usually handles updates from other threads via page.update() or control.update() if locking is correct.
        # However, it's safer to ensure we are thread-safe. Flet controls are generally thread-safe for property updates.
        self.timer_control.update_timer(remaining, total)

        # Update finish time based on remaining duration
        finish_time = datetime.now() + timedelta(seconds=remaining)
        new_text = finish_time.strftime("%H:%M")
        if self.finish_clock_text.value != new_text:
            self.finish_clock_text.value = new_text
            self.finish_clock_text.update()

    def on_timer_finish(self):
        # Execute Action
        config = self.timer_setup.get_configuration()
        result = ActionExecutor.execute(
            config["action"], self.process_selector.selected_processes
        )

        # UI Feedback
        # Note: Since this runs in the service thread, ensure UI calls are safe.
        # Flet page.open usually works from threads.

        if result["success"]:
            msg = result.get("message")
            if result.get("type") == "termination":
                count = result.get("count", 0)
                total = result.get("total", 0)
                if count == total:
                    msg = f"Successfully terminated {count} apps!"
                    bgcolor = "green700"
                elif count > 0:
                    msg = f"Terminated {count}/{total} apps."
                    bgcolor = "orange700"
                else:
                    msg = "Failed to terminate selected apps."
                    bgcolor = "red700"

                app_state.page.open(ft.SnackBar(content=ft.Text(msg), bgcolor=bgcolor))
            else:
                app_state.page.open(ft.SnackBar(content=ft.Text(msg)))
        else:
            app_state.page.open(
                ft.SnackBar(
                    content=ft.Text(result.get("message", "Error")), bgcolor="red700"
                )
            )

        self.reset_ui()

    def on_pause_click(self, e):
        # Service call will trigger listener update
        self.timer_service.toggle_pause()

    def on_cancel_click(self, e):
        self.timer_service.cancel_timer()
        app_state.page.open(ft.SnackBar(content=ft.Text("Timer cancelled.")))
        app_state.timer_config = {}  # Clear config
        self.reset_ui()

    def reset_ui(self):
        self.setup_container.visible = True
        self.timer_container.visible = False
        self.start_button.visible = True
        self.pause_button.visible = False
        self.cancel_button.visible = False
        self.timer_control.reset()
        self.update()
