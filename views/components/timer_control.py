import flet as ft


class TimerControl(ft.Stack):
    def __init__(self):
        super().__init__()
        self.progress_ring = ft.ProgressRing(
            width=200, height=200, stroke_width=15, value=0, color="blue500"
        )
        self.countdown_text = ft.Text("00:00:00", size=40, weight=ft.FontWeight.BOLD)
        self.percentage_text = ft.Text(
            "0%", size=12, weight=ft.FontWeight.BOLD, color="blue200"
        )
        self.paused_text = ft.Container(
            content=ft.Text(
                "PAUSED", size=12, weight=ft.FontWeight.BOLD, color="orange400"
            ),
            bgcolor="orange100",
            padding=ft.padding.symmetric(horizontal=8, vertical=2),
            border_radius=5,
            visible=False,
            margin=ft.margin.only(bottom=5),
        )

        self.controls = [
            self.progress_ring,
            ft.Container(
                content=ft.Column(
                    [
                        self.paused_text,
                        self.countdown_text,
                        self.percentage_text,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=0,
                ),
                # alignment=ft.alignment.center,
                width=200,
                height=200,
            ),
        ]

    def update_timer(self, remaining_seconds, total_seconds):
        mins, secs = divmod(remaining_seconds, 60)
        hours, mins = divmod(mins, 60)

        self.countdown_text.value = "{:02d}:{:02d}:{:02d}".format(hours, mins, secs)

        # Dynamic font sizing
        if len(self.countdown_text.value) > 8:
            self.countdown_text.size = 28
        else:
            self.countdown_text.size = 40

        if total_seconds > 0:
            self.progress_ring.value = remaining_seconds / total_seconds
            self.percentage_text.value = f"{int(self.progress_ring.value * 100)}%"
        else:
            self.progress_ring.value = 0
            self.percentage_text.value = "0%"

        self.update()

    def reset(self):
        self.countdown_text.value = "00:00:00"
        self.progress_ring.value = 0
        self.percentage_text.value = "0%"
        self.paused_text.visible = False
        self.update()

    def set_paused(self, paused: bool):
        self.paused_text.visible = paused
        self.update()
