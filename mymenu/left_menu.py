from py4web import URL
from .settings import APP_NAME

_app = APP_NAME
menu_str = f"{_app}/index"

def nav_item(item_nm, ctrl_nm):
    return item_nm, False, URL(f"{APP_NAME}/" + ctrl_nm)


l_menu = [
    ("Home", False, URL(menu_str), []),

    ( "Func", False, "#", [
            ("mi1", False, URL(f"{_app}/mi1")),
            ("upload", False, URL(menu_str)),
            ("tlist", False, URL(menu_str)),
        ],
    ),

    ( "Demo", False, "#", [
            ("mi2", False, URL(f"{_app}/mi2")),
            ("index", False, URL(menu_str)),
            ("mi3", False, URL(f"{_app}/mi3")),
            nav_item("yyy", "mi4"),
        ],
    ),
    ( "Setup", False, "#", [
            nav_item("x", "mi1"),
            nav_item("y", "mi2"),
            nav_item("z", "mi3"),
            nav_item("a", "mi4"),
        ],
    ),
]
