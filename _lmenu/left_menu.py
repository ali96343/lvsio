from py4web import URL
from .settings import APP_NAME

# the navigation menu from http://www.web2py.com/ 

b_menu = ''
t_menu = ''
l_menu = []

_url = APP_NAME + "/"
def nav_item(item_nm, ctrl_nm, flag= False):
    return item_nm, flag, URL( _url + ctrl_nm )

def ctrl_item(ctrl_nm, flag= False):
    item_nm = ctrl_nm
    for r in (("/", "_"), (".", "_")):
        item_nm = item_nm.replace(*r)
    return item_nm, flag, URL( _url + ctrl_nm )

def add_ctrl2nav(main_item, ctrl_nm, x_menu=l_menu):
    for e in x_menu:
        if e[0] != main_item:
            continue
        e[3].append( ctrl_item(ctrl_nm)  )
           

l_menu = [
    ("Home", False, URL(_url), []),

    ( "Func", False, "#", [
            ctrl_item('db_tables'),
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
            nav_item("t_menu", "mi6"),
            nav_item("b_menu", "mi5"),
        ],
    ),
]

#add_ctrl2nav('Func', 'mi5')
#add_ctrl2nav('Func', 'mi4')
#add_ctrl2nav('Func', 'mi3')
# ---------------------------------------------------

bb_menu = [

    ( "bb_x", False, "#", [
            ctrl_item('db_tables'),
            ("upload", False, URL(_url )),
            ("tlist", False, URL(_url )),
        ],
    ),
    ("X_1", False, URL(_url), []),
]


def button_menu( x_menu=l_menu  ):
    but_menu = []
    for _item in x_menu or []: 
      #print (_item)
      but_menu.append(f"<div>{_item[0]}</div>")
      if not _item[3]: 
          but_menu.append(f'<a role="button" href="{_item[2]}">{_item[0]}</a>' )
      for _ii in _item[3]: 
          but_menu.append(f'<a role="button" href="{_ii[2]}">{_ii[0]}</a>' )
    return ''.join( but_menu  ) 

b_menu = button_menu(  )
#b_menu = button_menu(  bb_menu  )

# ---------------------------------------------------
def table_menu( x_menu=l_menu  ):
    tab_menu = []
    tab_menu.append('<table class="table">')
    for _item in x_menu or []:
          tab_menu.append( 
             '<tr style="background: #e1e1e1">'
             + f'<th colspan="2" class="is-info">{_item[0]}</th>'
             + '</tr>'
          )
          if not _item[3]:
              tab_menu.append( 
                  '<tr>'
                  + f'<td>{_item[0]}</td>'
                  + f'<td><a role="button" href="{_item[2]}">go</a></td>'
                  + '</tr>'
              )

          for _ii in _item[3]:
              tab_menu.append( 
                  '<tr>'
                  + f'<td>{_ii[0]}</td>'
                  + f'<td><a role="button" href="{_ii[2]}">go</a></td>'
                  + '</tr>'
              )
    
    tab_menu.append('</table>')
    return ''.join( tab_menu  ) 

t_menu = table_menu()
