import threading
import time


class TimerService:
    def __init__(self):
        self._timer_thread = None
        self._running = False
        self._paused = False
        self._stop_event = threading.Event()
        self._tick_listeners = []
        self._finish_listeners = []
        self._pause_listeners = []

    def add_tick_listener(self, callback):
        if callback not in self._tick_listeners:
            self._tick_listeners.append(callback)

    def remove_tick_listener(self, callback):
        if callback in self._tick_listeners:
            self._tick_listeners.remove(callback)

    def add_finish_listener(self, callback):
        if callback not in self._finish_listeners:
            self._finish_listeners.append(callback)

    def remove_finish_listener(self, callback):
        if callback in self._finish_listeners:
            self._finish_listeners.remove(callback)

    def add_pause_listener(self, callback):
        if callback not in self._pause_listeners:
            self._pause_listeners.append(callback)

    def remove_pause_listener(self, callback):
        if callback in self._pause_listeners:
            self._pause_listeners.remove(callback)

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
        self._paused = False
        self._stop_event.clear()

        def run():
            remaining_seconds = total_seconds
            while remaining_seconds > 0 and not self._stop_event.is_set():
                if self._paused:
                    time.sleep(0.1)
                    continue

                if on_tick:
                    on_tick(remaining_seconds, total_seconds)

                for listener in self._tick_listeners:
                    try:
                        listener(remaining_seconds, total_seconds)
                    except Exception as e:
                        print(f"Error in tick listener: {e}")

                # Sleep in small chunks to allow faster cancellation response
                for _ in range(10):
                    if self._stop_event.is_set():
                        break
                    time.sleep(0.1)

                if not self._stop_event.is_set():
                    remaining_seconds -= 1

            self._running = False
            self._paused = False

            if not self._stop_event.is_set():
                # Timer finished naturally
                if on_tick:
                    on_tick(0, total_seconds)
                for listener in self._tick_listeners:
                    try:
                        listener(0, total_seconds)
                    except Exception:
                        pass

                if on_finish:
                    on_finish()
                for listener in self._finish_listeners:
                    try:
                        listener()
                    except Exception as e:
                        print(f"Error in finish listener: {e}")

        self._timer_thread = threading.Thread(target=run, daemon=True)
        self._timer_thread.start()

    def pause_timer(self):
        self._paused = True
        self._notify_pause_listeners()

    def resume_timer(self):
        self._paused = False
        self._notify_pause_listeners()

    def toggle_pause(self):
        self._paused = not self._paused
        self._notify_pause_listeners()
        return self._paused

    def is_paused(self):
        return self._paused

    def cancel_timer(self):
        """
        Cancels the currently running timer.
        """
        if self._running:
            self._stop_event.set()
            if self._timer_thread:
                self._timer_thread.join(timeout=1.0)
            self._running = False
            self._paused = False

    def is_running(self):
        return self._running

    def _notify_pause_listeners(self):
        for listener in self._pause_listeners:
            try:
                listener(self._paused)
            except Exception as e:
                print(f"Error in pause listener: {e}")
