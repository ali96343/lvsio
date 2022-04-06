from yatl.helpers import A, I, SPAN, XML, DIV, P, TABLE, THEAD, TR, TD, TBODY, H6, IMG
from py4web import action, request, response, abort, redirect, URL, Field
from .. common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.grid import Grid, GridClassStyle
from py4web.utils.form import Form, FormStyleDefault
from py4web.core import Template
from py4web import URL
import pydal
import copy

from py4web.utils.url_signer import URLSigner

#this_dir = os.path.dirname(os.path.realpath(__file__))
#sys.path.append( os.path.dirname(this_dir)   )

from .. settings import APP_NAME
from .. import chan_conf as C

#print ( APP_NAME  )


from yatl.helpers import UL, LI
from yatl.helpers import DIV, XML, TAG

def MENU(items):
      return UL(*[LI(name, 'xxxx', _href=link) if not other else LI(MENU(other)) for name, link, other in items])

# https://codetea.com/responsive-tables-using-li/
#print(  MENU(['One', False, 'link1'],  ) )

#Он создает элемент списка и должен содержаться в UL или OL тегах.

#>>> print LI('<hello>', XML('<b>world</b>'), _class='test', _id=0)
#<li id="0" class="test">&lt;hello&gt;<b>world</b></li>


#Обозначает неупорядоченный список и должен содержать элементы LI. 
# Если его содержание не помечено как LI, то UL делает это автоматически.

#>>> print UL('<hello>', XML('<b>world</b>'), _class='test', _id=0)
#<ul id="0" class="test"><li>&lt;hello&gt;</li><li><b>world</b></li></ul>

#Помощник MENU принимает список из списков или кортежей из формы 
#response.menu (как описано в главе 4) и создает древовидную структуру с 
#использованием неупорядоченных списков, представляющих меню. Например:

#>>> print MENU([['One', False, 'link1'], ['Two', False, 'link2']])
#<ul class="web2py-menu web2py-menu-vertical">
#  <li><a href="link1">One</a></li>
#  <li><a href="link2">Two</a></li>
#</ul>



@action("tlist_ul", method=["GET", "POST"])
@action.uses(flash, db, session, T, Template("myadm/tlist_ul.html", delimiters="[[ ]]"),)
def tlist_ul():
    ts=[ e for e in db.tables  ]
    
    cmd = [ '111', ]

    x= UL(* [ LI( A( f'{e}',  _href = URL( f"p4w_sql_table/{e}/{ee}") ) )   for e in ts   for ee in cmd  ]  )
    #print (x)

    t_vars = copy.deepcopy(C.html_vars)
    return locals()


@action("p4w_sql_table/<path:path>", method=["POST", "GET"])
def p4w_sql_table(path=None,):
    #user = auth.get_user()

    def get_param(ppath=None):
        if not ppath is None:
            if any([e in ppath for e in ("/details/", "/edit/", "/delete/", "/new")]):
                return ppath.split("/", 1)
            elif not "/" in path:
                return ppath, None
        return None, ppath

    str_path =  str( path.split('/') ) 
    return str_path






@action("tlist", method=["GET", "POST"])
@action.uses(flash, db, session, T, Template("myadm/tlist.html", delimiters="[[ ]]"),)
def tlist():
    ts=[ e for e in db.tables  ]
    headers= ['tname', 'tlen','cmd1', 'cmd2', 'cmd3']

    #flash.set("Hello World", sanitize=True)

    #cmd = ['111', '222', '333']
    def show_len(tn):
        c = db(db[tn].id>0).count()
        return f'{c}' if c else ''

    cmd = [ 
            lambda tn : show_len(tn) ,
            lambda tn : A( "table",  _role="button",  _href=URL( f"index",  ), ) ,
            lambda tn : A( "form",   _role="button",  _href=URL( f"index", ), ) , 
            lambda tn : A( "grid",   _role="button",  _href=URL( f"index",  ), ) ,
          ]

    cmd2 = [ 
            lambda tn : show_len(tn) ,
            lambda tn : A( "table",   _href=URL( f"index",  ), ) ,
            lambda tn : A( "form",    _href=URL( f"index", ), ) , 
            lambda tn : A( "grid",    _href=URL( f"index",  ), ) ,
          ]
    #w, h = len(cmd), len(ts);
    #Matrix = [[0 for x in range(w)] for y in range(h)] 

    Matrix = [[0 for x in range(1+ len( cmd ))] for y in range(  len(ts) )] 
    for i in range(len( ts  )):
        tnn = ts[i]
        for j in range(1 + len( cmd ) ):
           if j == 0:
               Matrix [i] [j] = tnn #ts[i]
           else:
               Matrix [i] [j] = cmd[j-1]( tnn  )

   

    x=  DIV( UL( * [  DIV( LI(f'{e}', _href=URL('xxx') )   ) for e in ts ] ) )

    x= UL(* [DIV( LI( A( f'{e}',  _href = URL('index') ) ) )   for e in ts ]  )
    x= UL(* [ LI( A( f'{e}',  _href = URL('index') ), DIV('job1') , DIV('job2') )    for e in ts ]  )

    x= UL(* [ DIV (  Matrix[y][x]    )   for y in range(len(ts))   for x in range(1+ len(cmd2))   ]    )
    print (x)
    
      
        
    #x = UL(*[LI(Matrix[y][x]) for x in range(1+ len(cmd))]) for y in range (len(ts)),
    #print (x)
    xview= DIV(
             SPAN(ts, _style="color:red"),
             TABLE(
                   #THEAD(TR(*[TD(H6(h)) for h in headers])),
                   TBODY(*[TR(*[TD(Matrix[y][x]) for x in range(1+ len(cmd))]) for y in range (len(ts))]),
                   ),
           )
    t_vars = copy.deepcopy(C.html_vars)
    message='tables:'
    #return 'hello! tlist'
    return locals()
    #return dict(message='tables:', xview=xview, response_menu=Xresponse_menu) 

#
#
#@action("mygrid", method=["GET", "POST"])
#def mygrid():
#    args = repr(dict(request.query))
#    return f"mygrid: {args}"
#
#@action("p4w_form", method=["GET", "POST"])
#def p4w_form():
#    args = repr(dict(request.query))
#    return f"p4w_form: {args}"
#
#@action("f1", method=["GET", "POST"])
#def f1():
#    args = repr(dict(request.query))
#    tbl = dict( request.query ).get('t_','') 
#    redirect( URL(  f"p4w_grid/{tbl}") )
#    
#    
#    return f"f1: {args}"
#
#@action("p4w_grid")
#@action("p4w_grid/<path:path>", method=["POST", "GET"])
#@action.uses(session, db, auth, "p4w_grid.html")
#def p4w_grid(path=None,):
#    def get_param(ppath=None):
#        if not ppath is None:
#            if any([e in ppath for e in ("/details/", "/edit/", "/delete/", "/new")]):
#                return ppath.split("/", 1)
#            elif not "/" in path:
#                return ppath, None
#        return None, ppath
#
#    #user = auth.get_user()
##
#    #if len(user):
#    #    message = "hello {first_name}".format(**user)
#    #else:
#    #    redirect(URL("tabadm"))
#    #print ( path )
#
#    tbl, path = get_param(path)
#
#    if not tbl in db.tables:
#        return f"bad table: {tbl}, path: {path}"
#
#    grid_param = dict(
#        rows_per_page=5,
#        include_action_button_text=False,
#        search_button_text="Filter",
#        formstyle=FormStyleDefault,
#        grid_class_style=GridClassStyle,
#    )
#
#    # labels=[ db[tbl][f].label for f in db[tbl].fields ]
#    search_queries = [
#        [db[tbl][f].label + " ~ ", lambda v: db[tbl][f].contains(v)]
#        for f in db[tbl].fields
#        if f != "id"
#    ]
#    search_queries.append(
#        ["id = ", lambda v: db[tbl].id == int(v) if v.isnumeric() else "error"]
#    )
#    query = db[tbl].id > 0
#    orderby = [db[tbl].id]
#    fields = [field for field in db[tbl] if field.readable]
#    grid = Grid(
#        path,
#        query,
#        fields=fields,
#        search_queries=search_queries,
#        orderby=orderby,
#        **grid_param,
#    )
#  
#    import datetime
# 
#    def re_fmt(tbl, cut_line = 10):
#        xfmt= dict()
#        for e in db[tbl].fields:
#           tmp_type = db[tbl][e].type
#           if tmp_type == 'datetime':
#              xfmt[ f"{tbl}.{e}"] = lambda e: SPAN( e.strftime(DATE_FORMAT), _style="color:red") 
#           elif any( [tmp_type == 'string', tmp_type == 'text'] ):
#               xfmt[ f"{tbl}.{e}"] = lambda e: SPAN(e[:FLD_LEN] + "~" if len(e) > FLD_LEN else e )
#           else:
#               xfmt[ f"{tbl}.{e}"] = lambda e: SPAN(e, _style="color:green" )
#           
#        return xfmt
#
#    #fmt = {f"{tbl}.{e}": lambda e: SPAN(e[:10] + "...") for e in db[tbl].fields }
#    fmt = re_fmt( tbl )
#    for k, v in fmt.items():
#        grid.formatters[k] = v
#    
#    #return dict(grid=grid, message=SPAN(f'{tbl}', _style="color:red"), response_menu=Xresponse_menu)
#    message=SPAN(f'{tbl}', _style="color:red")
#    t_vars = copy.deepcopy(C.html_vars)
#    return locals()
#
#
#@action("p4w_create_form", method=["GET", "POST"])
#@action("p4w_create_form/<path:path>", method=["GET", "POST"])
#@action.uses(session, db, auth, "p4w_create_form.html")
#def p4w_html_form(path=None, id=None):
#    #print ('form path: ', path)
#    if '/' in path:
#        path, id = path.split('/',1)
#    tbl = path
#    if not tbl in db.tables:
#        return f"bad table: {tbl}, path: {path}"
#    form = Form(db[tbl], id, deletable=False, formstyle=FormStyleDefault)
#
#    message=SPAN(f'{tbl}', _style="color:red")
#    t_vars = copy.deepcopy(C.html_vars)
#    return locals()
##    return dict(message=SPAN( tbl, _style="color:red"  ), form=form, response_menu=Xresponse_menu) 
#
#@action("p4w_sql_table", method=["GET", "POST"])
#@action("p4w_sql_table/<path:path>", method=["GET", "POST"])
#@action.uses(session, db, auth, "p4w_sql_table.html")
#def p4w_sql_table(path=None, id=None):
#    #print ('form path: ', path)
#    if '/' in path:
#        path, id = path.split('/',1)
#    tbl = path
#    if not tbl in db.tables:
#        return f"bad table: {tbl}, path: {path}"
#    form = Form(db[tbl], id, deletable=False, formstyle=FormStyleDefault)
#    mytab= sql2table( tbl,db , fld_skip=[] )
#
#    message=SPAN( tbl, _style="color:red"  )
#    t_vars = copy.deepcopy(C.html_vars)
#    return locals()
#    #return dict(message=SPAN( tbl, _style="color:red"  ), form=form, mytab=mytab,response_menu=Xresponse_menu )
#
#
