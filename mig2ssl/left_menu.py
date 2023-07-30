from py4web import URL
from .settings import APP_NAME

# the navigation menu from http://www.web2py.com/ 

l_menu = []

_url = APP_NAME + "/"
def menu_item(item_nm, route_nm):
    return item_nm, URL( _url + route_nm ), []

def route_item(route_nm):
    for r in ("/", "_"), (".", "_"):
        route_nm = route_nm.replace(*r)
    return route_nm, URL( _url + route_nm ), []

l_menu = [
    ("i", URL(_url), []),

    ( "Sio", "#", [
            route_item("index"),
            route_item("index"),
            route_item("index"),
        ],
    ),
    ( "Db", "#", [
            route_item("mi1"),
            route_item("mi2"),
            route_item("mi3"),
        ],
    ),
]


#print (l_menu)
