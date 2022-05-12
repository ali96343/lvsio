from py4web import action, request, response, abort, redirect, URL, Field
from py4web.utils.cors import CORS
from py4web.utils.form import Form, FormStyleDefault
from pydal.validators import IS_NOT_EMPTY
from yatl.helpers import A, DIV
from ..common import (
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
import logging, os, sys

from time import sleep
from datetime import datetime
import redis
import json

from itertools import count
generator_num = count(start=0, step = 1)


#
# https://github.com/ali96343/lvsio
#

from ..genhelpers import  threadsafe_generator

# https://github.com/jakubroztocil/chat/blob/master/app.py
# https://stackoverflow.com/questions/12232304/how-to-implement-server-push-in-flask-framework


from redis import StrictRedis
red = redis.StrictRedis()

RED_CHAT_CHAN="pchat_pchat_red"
TBL = "pchat_table"


def read_db(tbl=TBL):
    rs = db(db[tbl]).select()
    print(rs)


@action( "pchat_stream",)
@action.uses(session, CORS())
def pchat_stream():

    lastId = request.GET.get('lastId', 0 )
    try:
        lastId = int(lastId)
    except Exception as ex:
        #ex_template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        #ex_msg = ex_template.format(type(ex).__name__, ex.args)
        #print (ex_msg)
        lastId = 0

    #print ( lastId)


    @threadsafe_generator
    def generate_pchat():

        try:
            gen_id = str(next(generator_num) )

            pubsub = red.pubsub()
            pubsub.subscribe( RED_CHAT_CHAN )

            rs = db(db[TBL]).select( orderby=~ db[TBL].id, limitby=(0,5) )

            msgs = [ r['f0'] for r in rs ] if rs else []
            
            json_data = json.dumps( { 'msgs':msgs, 'gen_id': gen_id }  )

            last_event = lastId + 1
    
            while True:
    
                message = pubsub.get_message()

                if json_data:
                    yield f"event: pchat_start\ndata:{json_data}\n\n"
                    json_data = None

                if not message:
                    yield "data: {}\n\n"
                    sleep(0.2)
                    continue
    
                if message["type"] == "message":
                    yield "data: %s\nid: %s\n\n" % (message["data"].decode("utf-8"), 
                           last_event )
                    sleep(0.2)
                last_event += 1
    
        except Exception as ex:
                ex_template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                ex_msg = ex_template.format(type(ex).__name__, ex.args)
                print (ex_msg)
    
        finally:
            print ( f"finally: {sys._getframe().f_code.co_name}; id: {gen_id}" )

    response.headers["Content-Type"] = "text/event-stream"
    return generate_pchat()

@action("pchat_login", method=["GET", "POST"])
@action.uses("pchat/pchat_login.html", session, CORS())
def pchat_login():
    form = Form([Field("pchat_user", requires=IS_NOT_EMPTY())])
    if form.accepted:
        session["pchat_user"] = request.forms.get("pchat_user")
        redirect(URL("pchat_home"))
    return dict(form=form)

@action("pchat_post", method=["POST"])
@action.uses(session, CORS())
def pchat_post():

    command = request.forms.get("command")
    if command and command == 'truncate':
        db[TBL].truncate()
        db.commit()
        return 

    message = request.forms.get("message")
    user = session.get("pchat_user", "anonymous")
    now = datetime.now().replace(microsecond=0).time()

    f0 = "[%s] %s: %s" % (now.isoformat(), user, message)

    data_dict = {'f0': f0}
    db[TBL].validate_and_insert(**data_dict)
    db.commit()

    #red.publish( RED_CHAT_CHAN, "[%s] %s: %s" % (now.isoformat(), user, message))
    red.publish( RED_CHAT_CHAN, f0 )
    response.status = 204

#  204 No Content, the client doesn't need to navigate away from its current page.


@action("pchat_home", )
@action.uses('pchat/pchat.html',session, CORS())
def pchat_home():
    pchat_user = session.get("pchat_user")
    if pchat_user is None:
        redirect(URL("pchat_login"))

    return {  "url_index": URL("index"),
        "url_user_clear": URL("pchat_user_clear"),
        "url_pchat_stream": URL("pchat_stream"),
        "url_pchat_post": URL("pchat_post"),
        "chat_user": pchat_user, }

@action("pchat_user_clear")
@action.uses(session, CORS())
def pchat_user_clear():
    # session.clear()
    session["pchat_user"] = None
    redirect(URL("pchat_home"))

