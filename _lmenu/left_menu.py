from py4web import URL
from .settings import APP_NAME

# the navigation menu from http://www.web2py.com/ 

_url = APP_NAME + "/"

def nav_item(item_nm, ctrl_nm, flag= False):
    return item_nm, flag, URL( _url + ctrl_nm )

def ctrl_item(ctrl_nm, flag= False):
    item_nm = ctrl_nm
    for r in (("/", "_"), (".", "_")):
        item_nm = item_nm.replace(*r)
    return item_nm, flag, URL( _url + ctrl_nm )

def add_ctrl2nav(main_item, ctrl_nm):
    global l_menu 
    for e in l_menu:
        if e[0] != main_item:
            continue
        e[3].append( ctrl_item(ctrl_nm)  )
           

l_menu = [
    ("Home", False, URL(_url), []),

    ( "Func", False, "#", [
            ctrl_item('db_tables'),
            ctrl_item('ex1/ctrl1'),
            ("upload", False, URL(_url )),
            ("tlist", False, URL(_url )),
        ],
    ),

    ( "Demo", False, "#", [
            ctrl_item("mi2"),
            ("index", False, URL(_url )),
            ("mi3", False, URL(_url + "mi3" )),
            nav_item("yyy", "mi4"),
            ctrl_item("mi5"),
        ],
    ),

    ( "Grps", False, "#", [
            nav_item("manager", "find_tag/manager"),
            ctrl_item("find_tag/dancer"),
            ctrl_item("find_tag/teacher"),
            nav_item("z", "mi3"),
            nav_item("a", "mi4"),
            ctrl_item("mi5"),
        ],
    ),
]

add_ctrl2nav('Func', 'mi5')
add_ctrl2nav('Func', 'mi4')
add_ctrl2nav('Func', 'mi3')

