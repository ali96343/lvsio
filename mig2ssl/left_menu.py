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

    ( "Spa", "#", [
            route_item("spa-7531"),
            route_item("spa-67"),
            route_item("spa-55"),
            route_item("spa-45"),
            route_item("spa-364"),
            route_item("spa-324"),
            route_item("spa-300"),
        ],
    ),
    ( "Db", "#", [
            route_item("tlist"),
            route_item("mi2_db"),
            route_item("mi3_db"),
        ],
    ),

]


#print (l_menu)
