import os, json
from random import randint

from py4web import action
from py4web import URL, action, redirect, request
from py4web.utils.cors import CORS
from py4web.utils.factories import Inject

from ..helper import render_template

from ..settings import STATIC_FOLDER
try:
    from ..left_menu import l_menu
except ImportError:
    l_menu = []


MOD_FOLDER = os.path.dirname(__file__)
MOD_NAME = os.path.split(MOD_FOLDER)[-1]
STATIC_APP = 'client' 
SVELT_FOLDER = os.path.join(STATIC_FOLDER, f"{MOD_NAME}/{STATIC_APP}/public")
MOD_PATH=f"static/{MOD_NAME}/{STATIC_APP}/public"

print ( '===', STATIC_APP ,' ', MOD_NAME)

from ..common import db, session, T, cache, auth, logger



# ======================================================     e1 ====================================
# https://fjolt.com/article/svelte-pass-parameters-to-events


@action('index_e1')
def index_e1(): # index():
     # '`http://localhost:8000/svlt/message?name=${message}`'
     e1_message = URL( 'message_e1', scheme = True )
     e1_random = URL( 'random_e1', scheme = True )
     e1_json = URL( 'json_e1', scheme = True )
     d = dict(mod_path=MOD_PATH, some_param ='world', e1_message=e1_message, e1_random=e1_random, e1_json=e1_json )
     return render_template(d, 'p4w_index.html', path=SVELT_FOLDER)



@action('svlt_index')
@action.uses(session, T, db, )
def svlt_index(): # index():
     # '`http://localhost:8000/svlt/message?name=${message}`'
     message="svlt_index message"
     e1_message = URL( 'message_e1', scheme = True )
     e1_random = URL( 'random_e1', scheme = True )
     e1_json = URL( 'json_e1', scheme = True )
     d = dict(mod_path=MOD_PATH, some_param ='world', message=message, e1_message=e1_message, 
             l_menu=l_menu, e1_random=e1_random, e1_json=e1_json )
     return render_template(d, 'svlt_index.html', )


# curl -iL http://localhost:8000/svlt/message?name=manav
# curl -iL http://localhost:8000/svlt/message?
# curl -iL http://localhost:8000/svlt/message
# curl -iL http://localhost:8000/svlt/

@action("message_e1")
@action.uses(session, T, db, CORS() )
def message_e1(msg='error'):
    print ('request.query:',  request.query  )
    if not request.query:
        redirect(URL("message_e1", vars=dict(x=msg, y=2)))
    return repr(dict(request.query) if len(dict(request.query)) else dict (name='xxx!'))


@action("random_e1")
@action.uses(session, T, db, CORS() )
def random_e1():
    ret_value = str(randint(0, 100))
    print( ret_value ) 
    return ret_value 

@action("json_e1")
@action.uses(session, T, db, CORS() )
def json_e1():
    print (request)
    return json.dumps( [ {'a': 1, 'b':2, 'c': 3}, {'a': 11, 'b': 22, 'c': 33} ] )
