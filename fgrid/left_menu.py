from py4web import URL
from .settings import APP_NAME

# the navigation menu from http://www.web2py.com/ 

_url = APP_NAME + "/"

def nav_item(item_nm, route, flag= False):
    return item_nm, flag, URL( _url + route )

def ctrl_item(route, flag= False):
    item_nm = route
    #for r in (("/", "_"), (".", "_")):
    #    item_nm = item_nm.replace(*r)
    return item_nm, flag, URL( _url + route )

def add_ctrl2nav(main_item, route):
    global l_menu 
    for e in l_menu:
        if e[0] != main_item:
            continue
        e[3].append( ctrl_item(route)  )
           

l_menu = [
    ("Home", False, URL(_url), []),

    ( "Gs", False, "#", [
            ctrl_item("g1/editable_table"),
            ctrl_item("g1/server_table"),
            ctrl_item("g1/ajax_table"),
            ctrl_item("g1/basic_table"),
        ],
    ),

    ( "Grps", False, "#", [
            ctrl_item('db_tables'),
            ctrl_item("manager", "find_tag/manager"),
            ctrl_item("find_tag/dancer"),
            ctrl_item("find_tag/teacher"),
        ],
    ),
]

#add_ctrl2nav('Func', 'mi5')
#add_ctrl2nav('Func', 'mi4')
#add_ctrl2nav('Func', 'mi3')

