# Time to Sleep

> This is just a fun project built by vibe coding using Gemini 3 Pro. Expect many weird implementations

**Time to Sleep** is a modern, sleek Windows application designed to automatically terminate specific processes after a set duration. Built with Python and Flet, it offers a beautiful, dark-themed interface that looks great on your desktop.

## Features

*   **Modern UI**: Clean, dark-themed interface built with Flet.
*   **Process Discovery**: Lists running applications with their original icons.
*   **Smart Search**: Quickly find processes by name.
*   **Multi-Selection**: Select multiple applications to terminate simultaneously.
*   **Visual Feedback**: Clear visual indicators for selected processes and timer progress.
*   **Settings**: Toggle between Light/Dark mode and show/hide system processes.
*   **Portrait Mode**: Optimized for a compact, mobile-like window experience.

## Tech Stack

*   **Python 3.x**
*   **Flet**: For the Flutter-based UI.
*   **psutil**: For process management.
*   **Pillow (PIL)**: For image processing.
*   **pywin32**: For extracting executable icons.

## Installation

1.  Clone the repository.
2.  Create a virtual environment (recommended):
    ```bash
    python -m venv .venv
    .venv\Scripts\activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  Run the application:
    ```bash
    python main.py
    ```
2.  Select one or more processes from the list.
3.  Set the timer (Hours, Minutes, Seconds).
4.  Click **Start Timer**.
5.  Sit back! The selected applications will be closed automatically when the timer hits zero.

## Project Structure

*   `main.py`: Application entry point and navigation.
*   `state.py`: Shared application state management.
*   `process_manager.py`: Logic for listing and killing processes.
*   `icon_extractor.py`: Utility to extract icons from `.exe` files.
*   `views/`: Contains the UI components (`HomeView`, `SettingsView`).
*   `assets/`: Stores application assets (icons).

## Planned Features

*   **System Tray**: Add support for minimizing the application to the system tray.
*   **Gentle Notification**: Add support for gentle notifications when the timer is about to expire.
*   **More Actions**: Schedules
*   **More Triggers**: Do when CPU is idle, Do when battery is low, Do when Network is idle, Do when System is idle

## License

MIT License
