from py4web import action, request, response,  abort, redirect, URL
from py4web.utils.cors import CORS
from yatl.helpers import A, DIV
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from .settings import APP_NAME

# ----------------------

@action("index")
@action.uses("index.html", auth)
def index():
    user = auth.get_user()
    message = T("Hello {first_name}".format(**user) if user else "Hello")
    actions = {"allowed_actions": auth.param.allowed_actions}

    menu = DIV(
        DIV(
            A("stream_log", _role="button", _href=URL("stream_log",),),
            A("stream", _role="button", _href=URL("stream",),),
           ),
        DIV(
            A("sse_chat_home", _role="button", _href=URL("sse_chat_home",),),
            A("session/clear", _role="button", _href=URL("session/clear",),),
           ),
    )

    return locals()

from math import sqrt
from time import sleep

@action("stream_data", method=["GET", "POST"])
@action.uses(db, session, auth, T, CORS())
def stream_data():
    @threadsafe_generator
    def generate():
        for i in range(100):
            yield "{:.2f}\n".format(sqrt(i))
            sleep(1)
    return generate()


@action("stream", method=["GET", "POST"])
@action.uses(db, session, auth, T, CORS(),"stream.html")
# https://stackoverflow.com/questions/31948285/display-data-streamed-from-a-flask-view-as-it-updates/31951077#31951077
def stream():
    stream_url='/%s/stream_data' % APP_NAME
    #stream_url='http://127.0.0.1:8000/%s/stream_data' % APP_NAME
    return locals() 
    #, mimetype="text/plain")

# ---------------------------------------------------
import os
this_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(this_dir, "controllers.py")


@action("stream_log_data", method=["GET", "POST"])
@action.uses(db, session, auth, T, CORS())
def stream_log_data():
    @threadsafe_generator
    def generate():
        with open(file_path) as f:
            while True:
                yield f.read()
                sleep(1)
    return generate()

@action("stream_log", method=["GET", "POST"])
@action.uses(db, session, auth, T, CORS(),"stream_log.html")
# https://stackoverflow.com/questions/31948285/display-data-streamed-from-a-flask-view-as-it-updates/31951077#31951077
def stream_log():
    stream_url='/%s/stream_log_data' % APP_NAME
    #stream_url='http://127.0.0.1:8000/%s/stream_log_data' % APP_NAME
    return locals()

# --------------------------------------------------------------
import logging, os, sys

LOG_FILE = 'app.log'
log = logging.getLogger('__name__')
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG)

# 
# https://gist.github.com/platdrag/e755f3947552804c42633a99ffd325d4
import threading
'''
    A generic iterator and generator that takes any iterator and wrap it to make it thread safe.
    This method was introducted by Anand Chitipothu in http://anandology.com/blog/using-iterators-and-generators/
    but was not compatible with python 3. This modified version is now compatible and works both in python 2.8 and 3.0 
'''
class threadsafe_iter:
    """Takes an iterator/generator and makes it thread-safe by
    serializing call to the `next` method of given iterator/generator.
    """
    def __init__(self, it):
        self.it = it
        self.lock = threading.Lock()

    def __iter__(self):
        return self

    def __next__(self):
        with self.lock:
            return self.it.__next__()

def threadsafe_generator(f):
    """A decorator that takes a generator function and makes it thread-safe.
    """
    def g(*a, **kw):
        return threadsafe_iter(f(*a, **kw))
    return g



    #response.headers["Content-Type"] = 'text/event-stream'




# ------------------------ chat -----------------------
# https://github.com/jakubroztocil/chat
# https://maxhalford.github.io/blog/flask-sse-no-deps/


# https://maxhalford.github.io/blog/flask-sse-no-deps/
# https://github.com/MaxHalford/flask-sse-no-deps

import queue

class MessageAnnouncer:

    def __init__(self):
        self.listeners = []

    def listen(self):
        q = queue.Queue(maxsize=5)
        self.listeners.append(q)
        return q

    def announce(self, msg):
        for i in reversed(range(len(self.listeners))):
            try:
                self.listeners[i].put_nowait(msg)
            except queue.Full:
                del self.listeners[i]

announcer = MessageAnnouncer()

def format_sse(data: str, event=None) -> str:
    msg = f'data: {data}\n\n'
    if event is not None:
        msg = f'event: {event}\n{msg}'
    return msg


@action("ping", method=["GET", "POST"])
def ping():

    #session["counter"] = session.get("counter", 0) + 1
    #counter =  session.get("counter")


    msg = format_sse(data=f'pong')
    announcer.announce(msg=msg)
    response.status = 200
    #response.content_type = "application/json"
    return '' #, 200


@action("listen", method=["GET", "POST"])
def listen():

    @threadsafe_generator
    def generate():
        messages = announcer.listen()  # returns a queue.Queue
        while True:
            msg = messages.get()  # blocks until a new message arrives
            yield msg

    response.headers["Content-Type"] = 'text/event-stream'
    return generate() 


# --------------------------------------------------------------------
# https://stackoverflow.com/questions/12232304/how-to-implement-server-push-in-flask-framework


# ---------------------------- sse chat ----------------------------------------------------
# https://github.com/jakubroztocil/chat/blob/master/app.py
# https://stackoverflow.com/questions/12232304/how-to-implement-server-push-in-flask-framework


import datetime
import redis


red = redis.StrictRedis()


@threadsafe_generator
def sse_chat_event_stream():
    pubsub = red.pubsub()
    pubsub.subscribe('sse_chat_chat')
    # TODO: handle client disconnection.
    for message in pubsub.listen():
        #print (message)
        if message['type']=='message':
            yield 'data: %s\n\n' % message['data'].decode('utf-8')



#@app.route('/stream')
@action("sse_chat_stream", method=["GET",])
def sse_chat_stream():
    response.headers["Content-Type"] = 'text/event-stream'
    return sse_chat_event_stream() 
    #return flask.Response(event_stream(),
    #                      mimetype="text/event-stream")


#@app.route('/login', methods=['GET', 'POST'])
@action("sse_chat_login", method=["GET", "POST"])
@action.uses( session,  CORS())
def sse_chat_login():
    if request.method == 'POST':
        session['sse_chat_user'] = request.forms.get("sse_chat_user")
        print ( session['sse_chat_user']  )
        redirect(URL('sse_chat_home'))
    #if flask.request.method == 'POST':
    #    flask.session['user'] = flask.request.form['user']
    #    return flask.redirect('/')
    return '<form action="" method="post">user: <input name="sse_chat_user">'


#@app.route('/post', methods=['POST'])
@action("sse_chat_post", method=["GET", "POST"])
@action.uses( session,  CORS() )
def sse_chat_post():
    #message = flask.request.form['message']
     
    message = request.forms.get("message") 
    print (message)
    user = session.get('sse_chat_user', 'anonymous')  #flask.session.get('user', 'anonymous')
    now = datetime.datetime.now().replace(microsecond=0).time()
    red.publish('sse_chat_chat', u'[%s] %s: %s' % (now.isoformat(), user, message))
    response.status = 204
    return '204_response' #flask.Response(status=204)



@action("sse_chat_home", method=["GET","POST"])
@action.uses( session,  CORS() )
def sse_chat_home():
    #if 'user' not in flask.session:
    #    return flask.redirect('/login')
    #session['sse_chat_user'] = 'xxxxxxxx' 
    sse_chat_user = session.get( 'sse_chat_user' )
    #print ( session['sse_chat_user']  )     
    if sse_chat_user is None:
        redirect(URL("sse_chat_login"))
    return """
        <!doctype html>
        <title>sse_chat</title>
        <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js"></script>
        <style>body { max-width: 500px; margin: auto; padding: 1em; background: black; color: #fff; font: 16px/1.6 menlo, monospace; }</style>
        
         <form method="get" action="/%s/index">
             <button type="submit">menu</button>
         </form>

         <form method="get" action="/%s/session/clear">
             <button type="submit">del user</button>
         </form>

        <p><b>hi, %s!</b></p>
        <p>Message: <input id="in" /></p>
        <pre id="out"></pre>
        <script>
            function sse() {
                const source = new EventSource("/%s/sse_chat_stream");
                const out = document.getElementById('out');
                source.onmessage = function(e) {
                    // XSS in chat is fun (let's prevent that)
                    out.textContent =  e.data + '\\n' + out.textContent;
                };
            }
            $('#in').keyup(function(e){
                if (e.keyCode == 13) {
                    $.post('/%s/sse_chat_post', {'message': $(this).val()});
                    $(this).val('');
                }
            });
            sse();
        </script>
    """ %  ( APP_NAME, APP_NAME, sse_chat_user, APP_NAME, APP_NAME )   #flask.session['user']


@action("session/clear")
@action.uses(session)
def session_clear():
    session.clear()
    redirect(URL("sse_chat_home"))

