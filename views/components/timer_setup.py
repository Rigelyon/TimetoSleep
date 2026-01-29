import flet as ft
from datetime import datetime, timedelta
from state import app_state


class TimerSetup(ft.Column):
    def __init__(self, on_action_change=None):
        super().__init__()
        self.on_action_change = on_action_change

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
                ft.dropdown.Option("Shutdown"),
                ft.dropdown.Option("Restart"),
                ft.dropdown.Option("Lock"),
                ft.dropdown.Option("Sleep"),
            ],
            value="Terminate Process",
            on_change=self.on_action_change_handler,
            expand=True,
        )

        # Timer Inputs (Countdown)
        self.hours_input = ft.TextField(
            label="Hours",
            value="",
            width=80,
            text_align=ft.TextAlign.CENTER,
            keyboard_type=ft.KeyboardType.NUMBER,
            input_filter=ft.InputFilter(
                allow=True, regex_string=r"^[0-9]*$", replacement_string=""
            ),
            max_length=5,
        )
        self.minutes_input = ft.TextField(
            label="Mins",
            value="",
            width=80,
            text_align=ft.TextAlign.CENTER,
            keyboard_type=ft.KeyboardType.NUMBER,
            input_filter=ft.InputFilter(
                allow=True, regex_string=r"^[0-9]*$", replacement_string=""
            ),
            max_length=5,
        )
        self.seconds_input = ft.TextField(
            label="Secs",
            value="",
            width=80,
            text_align=ft.TextAlign.CENTER,
            keyboard_type=ft.KeyboardType.NUMBER,
            input_filter=ft.InputFilter(
                allow=True, regex_string=r"^[0-9]*$", replacement_string=""
            ),
            max_length=5,
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

        self.controls = [
            ft.Text("Action Settings:", weight=ft.FontWeight.BOLD),
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
            ft.Text("Timer Settings:", weight=ft.FontWeight.BOLD),
            self.countdown_inputs,
            self.specific_time_inputs,
        ]

    def on_timer_type_change(self, e):
        is_countdown = self.timer_type_dropdown.value == "Countdown"
        self.countdown_inputs.visible = is_countdown
        self.specific_time_inputs.visible = not is_countdown
        self.update()

    def on_action_change_handler(self, e):
        if self.on_action_change:
            self.on_action_change(self.action_dropdown.value)

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

        self.update()

    def get_total_seconds(self):
        total_seconds = 0
        if self.timer_type_dropdown.value == "Countdown":
            try:
                h = int(self.hours_input.value) if self.hours_input.value else 0
                m = int(self.minutes_input.value) if self.minutes_input.value else 0
                s = int(self.seconds_input.value) if self.seconds_input.value else 0
                total_seconds = h * 3600 + m * 60 + s
            except ValueError:
                return -1  # Invalid input
        else:  # Specific Time
            if not self.selected_time:
                return -2  # No time selected

            now = datetime.now()
            target_time = datetime.combine(now.date(), self.selected_time)

            if target_time <= now:
                # If time has passed today, assume tomorrow
                target_time += timedelta(days=1)

            diff = target_time - now
            total_seconds = int(diff.total_seconds())

        return total_seconds
