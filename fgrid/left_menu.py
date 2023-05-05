from py4web import URL
from .settings import APP_NAME
from py4web.utils.url_signer import URLSigner

from .g2 import url_signer_no_session
from .t1 import url_t_signer 


# the navigation menu from http://www.web2py.com/ 

_url = APP_NAME + "/"

def nav_item(item_nm="", route="", flag= False):
    return item_nm, flag, URL( _url + route )

def ctrl_item(route, flag= False):
    item_nm = route
    #for r in (("/", "_"), (".", "_")):
    #    item_nm = item_nm.replace(*r)
    return item_nm, flag, URL( _url + route )


def ctrl_item_sign(route, x_sign, flag= False,):
    item_nm = route
    #for r in (("/", "_"), (".", "_")):
    #    item_nm = item_nm.replace(*r)
    return item_nm, flag, URL( _url + route, signer = x_sign )



def add_ctrl2nav(main_item, route):
    global l_menu 
    for e in l_menu:
        if e[0] != main_item:
            continue
        e[3].append( ctrl_item(route)  )
           

l_menu = [
    # ("Home", False, URL(_url), []),

    ( "g1", False, "#", [
            ctrl_item("g1/editable_table"),
            ctrl_item("g1/server_table"),
            ctrl_item("g1/ajax_table"),
            ctrl_item("g1/basic_table"),
        ],
    ),

    ( "g2", False, "#", [
            ctrl_item("g2/editable_table"),
            ctrl_item("g2/server_table"),
            ctrl_item("g2/ajax_table"),
            #ctrl_item("g2/basic_table"),
            ctrl_item_sign("g2/basic_table", url_signer_no_session),
        ],
    ),

    ( "t1", False, "#", [
            ctrl_item("t1/server_table"),
            ctrl_item("t1/ajax_table"),
            ctrl_item("t1/basic_table"),
        ],
    ),

    ( "t2", False, "#", [
            ctrl_item("t2/basic_table_ex3"),
            ctrl_item("t2/basic_table_ex2"),
            ctrl_item("t2/basic_table_ex1"),
            ctrl_item("t2/basic_table"),
        ],
    ),




    ( "Grps", False, "#", [
            ctrl_item('db_tables'),
            nav_item("manager", "find_tag/manager"),
            ctrl_item("find_tag/dancer"),
            ctrl_item("find_tag/teacher"),
        ],
    ),
]

#add_ctrl2nav('Func', 'mi5')
#add_ctrl2nav('Func', 'mi4')
#add_ctrl2nav('Func', 'mi3')

