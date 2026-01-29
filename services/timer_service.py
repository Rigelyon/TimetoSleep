import threading
import time


class TimerService:
    def __init__(self):
        self._timer_thread = None
        self._running = False
        self._stop_event = threading.Event()

    def start_timer(self, total_seconds, on_tick, on_finish):
        """
        Starts a countdown timer in a separate thread.

        Args:
            total_seconds (int): Duration of the timer in seconds.
            on_tick (callable): Callback function called every second with (remaining_seconds, total_seconds).
            on_finish (callable): Callback function called when the timer reaches 0.
        """
        if self._running:
            return

        self._running = True
        self._stop_event.clear()

        def run():
            remaining_seconds = total_seconds
            while remaining_seconds > 0 and not self._stop_event.is_set():
                if on_tick:
                    on_tick(remaining_seconds, total_seconds)

                # Sleep in small chunks to allow faster cancellation response
                for _ in range(10):
                    if self._stop_event.is_set():
                        break
                    time.sleep(0.1)

                if not self._stop_event.is_set():
                    remaining_seconds -= 1

            self._running = False

            if not self._stop_event.is_set():
                # Timer finished naturally
                if on_tick:
                    on_tick(0, total_seconds)
                if on_finish:
                    on_finish()

        self._timer_thread = threading.Thread(target=run, daemon=True)
        self._timer_thread.start()

    def cancel_timer(self):
        """
        Cancels the currently running timer.
        """
        if self._running:
            self._stop_event.set()
            if self._timer_thread:
                self._timer_thread.join(timeout=1.0)
            self._running = False

    def is_running(self):
        return self._running
