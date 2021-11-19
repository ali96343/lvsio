from py4web import action, request, abort, redirect, URL
from yatl.helpers import A, I, SPAN, XML, DIV, P
from py4web import action, request, response, abort, redirect, URL, Field
from py4web.utils.form import Form, FormStyleBulma
import inspect
import copy


from .common import (
    db,
    session,
    T,
    cache,
    auth,
    logger,
    authenticated,
    unauthenticated,
    flash,
)


from .settings import APP_NAME
# import ombott  

import os, sys

import socketio
import datetime
import json
from random import randrange


from . import chan_conf as C

r_mgr = socketio.RedisManager(C.r_url, write_only=True, channel=C.sio_channel)


html_vars = {
    "sio_serv_url": C.sio_serv_url,
    "sio_app": C.P4W_APP,
    "sio_port": C.sio_PORT,
}


def read_db(tbl='my_tbl'):
    rs = db( db[tbl] ).select()
    print (rs)
     

#read_db('Counter')
#read_db('ImaSize')
#read_db('Autocomplete')
#read_db('Sliders')


@action("sio_pusher", method=["GET", ])
def sio_pusher():
    data_str = datetime.datetime.now().strftime("%d.%m.%y %H:%M:%S")
    r_mgr.emit('pgs_reload',  data_str, broadcast=True, include_self=False )
    return None


@unauthenticated("index", "index.html")
def index():
    user = auth.get_user()
    message = T("Hello {first_name}".format(**user) if user else "Hello")
    actions = {"allowed_actions": auth.param.allowed_actions}

    menu = DIV(
        P("from pydal to js-UI with socketio"),
        DIV(
            A("js_image_resize", _role="button", _href=URL("js_image_resize",),),
            A("js_count", _role="button", _href=URL("js_count",),),
            A("js_sutocomplete", _role="button", _href=URL("js_autocomplete",),),
            A("js_sliders", _role="button", _href=URL("js_sliders",),),
        ),
    )

    return dict(message=message, actions=actions, menu=menu)


@action("js_autocomplete", method=["GET", "POST"])
@action.uses(db, session, auth, T, "js-autocomplete.html")
def js_autocomplete():
    t_vars = copy.deepcopy(html_vars)
    tbl = 'Autocomplete'
    countries = [ e.f0 for e in db( db[tbl] ).select()  ]

    f_autocomplete = Form(db[tbl], dbio=False, formstyle=FormStyleBulma)
    if f_autocomplete.accepted:
        f0 = f_autocomplete.vars.get('f0' )
        auth.flash.set(f'f0={f0}', sanitize=True)
    elif f_autocomplete.errors:
        print(f"f_autocomplete has errors: {f_autocomplete.errors}")

    t_vars['tnm'] = tbl
    return locals()

@action("js_sliders", method=["GET", "POST"])
@action.uses(db, session, T, "js-sliders.html")
def js_sliders():
    t_vars = copy.deepcopy(html_vars)

    tbl = "Sliders"
    r = db(db[tbl].id == 1).select().first()
    t_vars["slider1"] = r.f0 if r else 404 
    t_vars["slider2"] = r.f1 if r else 404 
    t_vars["txt1"] = r.f2 if r else '404' 

    flds =  [ e for e in  db[tbl].fields if e !='id' ] 
    vars_list = [ db[tbl][1][e]  for e in  flds ]
    t_vars["vars"] = json.dumps({ 'vars': vars_list  }  )
    t_vars['_fi_'] = sys._getframe().f_code.co_name
    return locals()




# ------------------------------------------------------------------------

def str2type(s, dst_type):

       if dst_type == 'integer':
           res = 0
           try:
               res = int(s)
               if res < 0: 
                    res = 0
               if res > 100: 
                    res = 100
           except Exception as ex:
               res = 0
               print ('ex dst_type: ',ex)
       elif dst_type == 'string':
           res = ''
           cut_len = 250
           try:
              res = (s[:cut_len] + '..') if s and len(s) > cut_len else s
           except Exception as ex:
               res = 'string 404!'
               print (ex)
       else:
           res = 0
           fname = sys._getframe().f_code.co_name
           print (f'{fname}: unk type! {dst_type}')
       return res
            
# ------------------------------------------------------------------------

def do_event(*args, **kwargs):
    tbl = kwargs['t_name'] #'Counter'

    flds =  [ e for e in  db[tbl].fields if e !='id' ]
    ftypes =  [ db[tbl][e].type for e in  flds ]

    data_dict = { f'f{i}': str2type(e, ftypes[i])  for i, e in enumerate( args) }

    db(db[tbl].id == 1).update(**db[tbl]._filter_fields(data_dict))
    db.commit()

    vars_list =  [ db[tbl][1][e]  for e in  flds ]

    json_data = json.dumps({ 'vars': vars_list }  )
    r_mgr.emit(kwargs['update'], json_data, broadcast=True, include_self=False)


allow_post = { 'js_image_resize', 'js_count', 'js_sliders'  }
ev2update = { 'js_image_resize': 'update_image', 'js_count': 'update_counter', 'js_sliders': 'update_sliders'  }
ev2table = { 'js_image_resize': 'ImaSize', 'js_count': 'Counter', 'js_sliders': 'Sliders'  }


@action("js_image_resize", method=["GET", "POST"])
@action.uses(db, session, T, "js-image-resize.html")
def js_image_resize():
    t_vars = copy.deepcopy(html_vars)
    tbl = "ImaSize"
    r = db(db[tbl].id == 1).select().first()
    t_vars["value"] = r.f0 if r else 44 
    t_vars['_fi_'] = sys._getframe().f_code.co_name
    return locals()


@action("js_count", method=["GET", "POST"])
@action.uses(db, session, T, "js-count.html")
def js_count():
    t_vars = copy.deepcopy(html_vars)
    tbl = "Counter"
    r = db(db[tbl].id == 1).select().first()
    t_vars["value"] = r.f0 if r else 404 
    t_vars['_fi_'] = sys._getframe().f_code.co_name
    return locals()


@action("sio_chan_post", method=["POST", ])
@action.uses()
def sio_chan_post():

    try:
        json_data = json.loads(request.body.read())

        event_name = json_data["event_name"]
        room = json_data["room"]
        data = json_data["data"]
            
        if json_data["broadcast_secret"] == C.POST_SECRET:
            cat_value = ""  # request.get_header('app-param')
            cat_value = request.headers.get("app-param", "xxxxxxxx")
            # C.sio_debug and print("from sio_chan_post header: ", cat_value)
            # C.sio_debug and print("json-post-data: ", json_data)
            if not event_name in allow_post:
                 print ('=== bad event === ', event_name )
                 print ( json_data  )
            else:
                 update_key= ev2update[event_name]
                 t_name = ev2table[event_name]
                 js_data = data.get('data')
                 if isinstance( js_data, list ):
                     do_event( *js_data,  update=update_key, t_name=t_name )
                 else:
                     do_event( js_data,  update=update_key, t_name=t_name )

    except Exception as ex:
        print("ex! sio_chan_post: ", ex)
        print(sys.exc_info())
        return "bad"

    return "ok"


