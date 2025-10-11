import flet as ft
import json


def main(page: ft.Page):
    page.fonts = {"Jose": "Fonts/font4.ttf"}
    page.theme = ft.Theme(font_family="Jose")
    page.title = "EndoBotM Control Panel"
    page.window.resizable = False
    page.window.maximizable = False

    # Fake client data
    clients = '{"client": 1, "hostname": "ENDOSPC", "ip": "192.168.1.1"}'
    client = json.loads(clients)

    selected_client = ft.Ref[str]()
    selected_client.value = None

    home_view = ft.Container(
        padding=10,
        content=ft.Column(
            controls=[
                ft.Text(
                    "Server Side Control Panel", size=30, weight=ft.FontWeight.BOLD
                ),
                ft.Text("i am a subtitle", size=11),
                ft.Text("im also a subtitle but slightly shorter", size=10),
            ],
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.START,
        ),
    )

    detail_title = ft.Text("", size=22, weight=ft.FontWeight.BOLD)

    def show_client_grid(e=None):
        client_grid.visible = True
        detail_view.visible = False
        page.update()

    def show_client_details(client_name, e=None):
        selected_client.value = client_name
        detail_title.value = f"Client {client_name} — Control Center"
        client_grid.visible = False
        detail_view.visible = True
        page.update()

    client_grid = ft.Container(
        content=ft.GridView(
            expand=1,
            runs_count=5,
            spacing=10,
            run_spacing=10,
            controls=[
                ft.ElevatedButton(
                    text=f"{int(client['client']) + i}",
                    on_click=lambda e, c=f"{int(client['client']) + i}": show_client_details(
                        c, e
                    ),
                    style=ft.ButtonStyle(
                        padding=10, shape=ft.RoundedRectangleBorder(radius=8)
                    ),
                )
                for i in range(20)
            ],
        ),
        border_radius=8,
        height=650,
    )

    back_button = ft.ElevatedButton(
        "Back to Clients",
        icon=ft.Icons.ARROW_BACK_ROUNDED,
        on_click=show_client_grid,
        style=ft.ButtonStyle(padding=20),
    )

    def make_detail_tabs():
        return ft.Tabs(
            selected_index=0,
            animation_duration=200,
            tabs=[
                ft.Tab(
                    text="Remote Terminal",
                    icon=ft.Icons.TERMINAL_ROUNDED,
                    content=ft.Text("Terminal interface goes here."),
                ),
                ft.Tab(
                    text="Screen View",
                    icon=ft.Icons.REMOVE_RED_EYE,
                    content=ft.Text("Live screen stream view placeholder."),
                ),
                ft.Tab(
                    text="File Transfer",
                    icon=ft.Icons.DRIVE_FOLDER_UPLOAD_ROUNDED,
                    content=ft.Text("File management interface placeholder."),
                ),
                ft.Tab(
                    text="Detailed Info",
                    icon=ft.Icons.SCREEN_SEARCH_DESKTOP_ROUNDED,
                    content=ft.Text("Detailed client system info."),
                ),
                ft.Tab(
                    text="Misc. Features",
                    icon=ft.Icons.MISCELLANEOUS_SERVICES,
                    content=ft.Text("Random utilities placeholder."),
                ),
            ],
            expand=1,
        )

    detail_view = ft.Container(
        visible=False,
        content=ft.Column(
            controls=[back_button, detail_title, make_detail_tabs()],
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            expand=True,
        ),
    )

    clients_screen = ft.Container(
        content=ft.Column(controls=[client_grid, detail_view], expand=True),
        padding=10,
    )

    content_holder = ft.Container(expand=1, content=home_view)

    def change_rail(index: int):
        if index == 0:
            content_holder.content = home_view
        elif index == 1:
            content_holder.content = clients_screen
        else:
            content_holder.content = ft.Text(f"Unknown index: {index}")
        page.update()

    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=75,
        group_alignment=-0.9,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.HOME_OUTLINED,
                selected_icon=ft.Icons.HOME_ROUNDED,
                label="Home",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icon(ft.Icons.GROUPS_3_OUTLINED),
                selected_icon=ft.Icon(ft.Icons.GROUPS_3_ROUNDED),
                label="Clients",
            ),
        ],
        on_change=lambda e: change_rail(e.control.selected_index),
    )
    page.add(
        ft.Row(
            [
                rail,
                ft.VerticalDivider(width=1),
                ft.Column(
                    [content_holder], alignment=ft.MainAxisAlignment.START, expand=True
                ),
            ],
            expand=True,
        )
    )

    page.update()


ft.app(main)
