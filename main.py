import flet as ft
from views.home_view import HomeView
from views.settings_view import SettingsView
from state import app_state


def main(page: ft.Page):
    app_state.set_page(page)

    page.title = "Time to Sleep"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.window.width = 500
    page.window.height = 750
    page.window.resizable = True
    page.update()

    # Views
    home_view = HomeView()
    settings_view = SettingsView()

    def on_nav_change(e):
        index = e.control.selected_index
        home_view.visible = index == 0
        settings_view.visible = index == 1
        page.update()

    page.navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon="home", label="Home"),
            ft.NavigationBarDestination(icon="settings", label="Settings"),
        ],
        on_change=on_nav_change,
    )

    # Layout Assembly
    page.add(ft.Column([home_view, settings_view], expand=True))


if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")
