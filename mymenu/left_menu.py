from py4web import URL
from .settings import APP_NAME

# the menu navigation file is borrowed from web2py

app_url = f"{APP_NAME}/"

def nav_item(item_nm, ctrl_nm, flag= False):
    return item_nm, flag, URL( app_url + ctrl_nm )


l_menu = [
    ("Home", False, URL(app_url), []),

    ( "Func", False, "#", [
            ("mi1", False, URL(app_url + "mi1")),
            ("upload", False, URL(app_url )),
            ("tlist", False, URL(app_url )),
        ],
    ),

    ( "Demo", False, "#", [
            nav_item("mi2", "mi2"),
            ("index", False, URL(app_url )),
            ("mi3", False, URL(app_url + "mi3")),
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
