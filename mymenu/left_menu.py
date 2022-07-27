from py4web import URL
from .settings import APP_NAME

ctrl_pref = f"{APP_NAME}/"

def nav_item(item_nm, ctrl_nm, flag= False):
    return item_nm, flag, URL( ctrl_pref  + ctrl_nm)


l_menu = [
    ("Home", False, URL(ctrl_pref), []),

    ( "Func", False, "#", [
            ("mi1", False, URL(ctrl_pref + "mi1")),
            ("upload", False, URL(ctrl_pref )),
            ("tlist", False, URL(ctrl_pref )),
        ],
    ),

    ( "Demo", False, "#", [
            ("mi2", False, URL(ctrl_pref + "mi2")),
            ("index", False, URL(ctrl_pref )),
            ("mi3", False, URL(ctrl_pref + "mi3")),
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
