from py4web import action, request, response, abort, redirect, URL
from py4web.utils.cors import CORS
from yatl.helpers import A, DIV
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
import logging, os, sys

from math import sqrt
from time import sleep
from datetime import datetime
import redis
import json
import random
import threading


# -------------------------------------------------------------------------

# ./py4web.py run apps --watch=off -s wsgirefThreadingServer

# vi ../../py4web/server_adapters.py
#            class ThreadingWSGIServer(PoolMixIn, WSGIServer):
#                daemon_threads = True
#                pool = ThreadPoolExecutor(max_workers=4000)
#                                          ^^^^^^^^^^^^^^^^

# --------------------------------------------------------------------------


import threading
from contextlib import contextmanager


# https://stackoverflow.com/quepython stions/16740104/python-lock-with-statement-and-timeout


class TimeoutLock:
    def __init__(self):
        self._lock = threading.Lock()

    def acquire(self, blocking=True, timeout=-1):
        return self._lock.acquire(blocking, timeout)

    @contextmanager
    def acquire_timeout(self, timeout):
        result = self._lock.acquire(timeout=timeout)
        yield result
        if result:
            self._lock.release()

    def release(self):
        self._lock.release()


# Usage:
"""
lock = TimeoutLock()

with lock.acquire_timeout(3) as result:
    if result:
        print('got the lock')
        # do something ....
    else:
        print('timeout: lock not available')
        # do something else ...
"""


# https://eli.thegreenplace.net/2011/08/22/how-not-to-set-a-timeout-on-a-computation-in-python


'''
class TimeLimitExpired(Exception): pass

def timelimit(timeout, func, args=(), kwargs={}):
    """ Run func with the given timeout. If func didn't finish running
        within the timeout, raise TimeLimitExpired
    """
    import threading
    class FuncThread(threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
            self.result = None

        def run(self):
            self.result = func(*args, **kwargs)

    it = FuncThread()
    it.start()
    it.join(timeout)
    if it.isAlive():
        raise TimeLimitExpired()
    else:
        return it.result

'''

# SuperFastPython.com
# example of a thread-safe list
from threading import Lock

# custom class wrapping a list in order to make it thread safe
class ThreadSafeList:
    # constructor
    def __init__(self):
        self._list = list()
        self._lock = Lock()

    # add a value to the list
    def append(self, value):
        with self._lock:
            self._list.append(value)

    # search value in list
    def check(self, value):
        with self._lock:
            return value in self._list

    def remove(self, value):
        with self._lock:
            # append the value
            self._list.remove(value)

    # remove and return the last value from the list
    def pop(self):
        with self._lock:
            return self._list.pop()

    # read a value from the list at an index
    def get(self, index):
        # acquire the lock
        with self._lock:
            # read a value at the index
            return self._list[index]

    # return the number of items in the list
    def length(self):
        # acquire the lock
        with self._lock:
            return len(self._list)


yield_id_list = ThreadSafeList()
import uuid


#
# https://github.com/ali96343/lvsio
#

# ---------------------------------------------------------------------------

# https://gist.github.com/platdrag/e755f3947552804c42633a99ffd325d4

"""
    A generic iterator and generator that takes any iterator and wrap it to make it thread safe.
    This method was introducted by Anand Chitipothu in http://anandology.com/blog/using-iterators-and-generators/
    but was not compatible with python 3. This modified version is now compatible and works both in python 2.8 and 3.0
"""


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
    """A decorator that takes a generator function and makes it thread-safe."""

    def g(*a, **kw):
        return threadsafe_iter(f(*a, **kw))

    return g


# -----------------------------------------------------------------------------

import ombott

def before_request():
    print ('11111111111111 ==============================')
    print ('+++',response)
    print ('---',request)
    print ( ombott.HTTPResponse.body  )
    print ( response.body  )
    print ("Response status {}".format(response.status_code) )

#ombott.default_app().add_hook( "before_request", before_request )

def after_request():
    print ('2222222222222 ==============================')
    print ('+++',response)
    print ('---',request)
    print ( ombott.HTTPResponse.body  )
    print ( response.body  )
    print ("Response status {}".format(response.status_code) )

#ombott.default_app().add_hook( "after_request", after_request )


# ----------------------------------------------------------------------------




@action("index")
@action.uses("index.html", auth)
def index():
    user = auth.get_user()
    message = T(
        "Hello {first_name}".format(**user) if user else "sse with wsgirefThreadingServer (or waitress)"
    )
    actions = {"allowed_actions": auth.param.allowed_actions}

    menu = DIV(
        DIV(
            A(
                "stream_log",
                _role="button",
                _href=URL(
                    "stream_log",
                ),
            ),
            A(
                "stream_sqrt pydal",
                _role="button",
                _href=URL(
                    "stream_sqrt",
                ),
            ),
            A(
                "stream_sqrt_id",
                _role="button",
                _href=URL(
                    "stream_sqrt_id",
                ),
            ),
        ),
        DIV(
            A(
                "sse_time",
                _role="button",
                _href=URL(
                    "sse_time",
                ),
            ),
        ),
        DIV(
            A(
                "hello-wasm",
                _role="button",
                _href=URL(
                    "hello-wasm",
                ),
            ),
        ),
        DIV(
            A(
                "sse_chat_home",
                _role="button",
                _href=URL(
                    "sse_chat_home",
                ),
            ),
            A(
                "user_clear",
                _role="button",
                _href=URL(
                    "sse_chat_user_clear",
                ),
            ),
        ),
        # DIV( # this task does not work, need fix
        #    A("pubsub_root", _role="button", _href=URL("pubsub_root",),),
        # ),
        DIV(
            A(
                "sse_chart",
                _role="button",
                _href=URL(
                    "sse_chart",
                ),
            ),
            A(
                "sse_progress",
                _role="button",
                _href=URL(
                    "sse_progress",
                ),
            ),
        ),
    )

    return locals()


# ------------------- hello-wasm --------------------------

# https://developer.mozilla.org/en-US/docs/WebAssembly/Rust_to_wasm
# http://arahna.de/rust-webassembly/
# https://dev.to/tuned/rust-scales-python-basic-experiment-49h0
# https://github.com/Mec-iS/rust-wasm-python-101/tree/0ad1a42f637d505bac8cf02e594be122900ec2c2
# https://thenewstack.io/using-web-assembly-written-in-rust-on-the-server-side/
# https://github.com/reselbob/wisesayingswasm

@action('hello-wasm')
@action.uses('hello-wasm.html')
def hello_wasm():
    hello_url=URL('static/pkg/hello_wasm.js')
    return locals()



# ------------------- task 1 : sqrt numbers ------------------------------------

# http://unixnme.blogspot.com/2017/10/thread-safe-generators-in-python.html


@threadsafe_generator
def id_generator(n):
    result = 1
    while True:
        if result >= n:
            result = 1
        yield result
        result += 1


id_gen = id_generator(100)


def read_db(tbl="my_tbl"):
    rs = db(db[tbl]).select()
    print(rs)


# read_db('sse_sqrt_value')


@action("stream_sqrt_data", method=["GET", "POST"])
@action.uses(db, session, auth, T, CORS())
def stream_sqrt_data():

    tbl = "sse_sqrt_value"

    @threadsafe_generator
    def generate():

        some_id = next(id_gen)
        print(some_id)

        for i in range(100):

            data_dict = {"f0": i}

            try:
                rx = db(db[tbl].id == some_id).select().first()
                if rx:
                    # db(db[tbl].id == some_id ).update (**db[tbl]._filter_fields(data_dict))
                    ret = db(db[tbl].id == some_id).validate_and_update(**data_dict)
                else:
                    # some_id = db[tbl].insert(**db[tbl]._filter_fields(data_dict))
                    some_id = db[tbl].validate_and_insert(**data_dict)

                # db(db[tbl].id == some_id ).update (f0 = i)
                db.commit()
            except Exception as e:
                print(e)
            r = db(db[tbl].id == some_id).select().first()
            print(r)
            yield "{:.2f}\n".format(sqrt(r["f0"]))
            # yield "{:.2f}\n".format(sqrt(i))
            try:
                db(db[tbl].id == some_id).update(f0=99999999999999999)
                db.commit()
            except Exception as e:
                print(e)
            sleep(1)

    return generate()


@action("stream_sqrt", method=["GET", "POST"])
@action.uses(
    "stream_sqrt.html",
    db,
    session,
    auth,
    T,
    CORS(),
)
# https://stackoverflow.com/questions/31948285/display-data-streamed-from-a-flask-view-as-it-updates/31951077#31951077
def stream_sqrt():
    stream_url = URL("stream_sqrt_data")
    menu_url = URL("index")
    return locals()


# stream_time -------------------------------------------------------------


@action("sse_time_data", method=["GET", "POST"])
@action.uses(session, auth, T, CORS())
def sse_time_data():

    # ./py4web.py run apps --watch=off -s wsgirefThreadingServer

    @threadsafe_generator
    def generate():
        num = 0

        try:

            while True:
                # print(num); num += 1

                json_data = json.dumps(
                    {
                        "time": datetime.now().strftime("%H:%M:%S.%f")[:-3],
                        "value": round(random.random() * 100, 2),
                    }
                )
                response.headers["Content-Type"] = "text/event-stream"
                yield f"data:{json_data}\n\n"
                sleep(1)

        finally:
            print("time-finally")

    return generate()


@action("sse_time", method=["GET", "POST"])
@action.uses(
    "sse_time.html",
    db,
    session,
    auth,
    T,
    CORS(),
)
def sse_time():
    stream_url = URL("sse_time_data")
    menu_url = URL("index")
    return locals()


# ------------------------------------------------------------------------


@action("stream_sqrt_id_data", method=["GET", "POST"])
@action.uses(session, auth, T, CORS())
def stream_sqrt_id_data():

    yield_id = str(uuid.uuid4())
    yield_id_list.append(yield_id)

    # print(yield_id)

    @threadsafe_generator
    def generate():
        try:

            for i in range(30):

                json_data = json.dumps(
                    {
                        "time": datetime.now().strftime("%d.%m.%y %H:%M:%S"),
                        "value": f"{sqrt(i):.2f}",
                        "yield_id": yield_id,
                    }
                )

                # print(json_data)
                yield f"{json_data}\n\n"

                if not yield_id_list.check(yield_id):
                    break

                # yield "{:.2f}\n\n".format(sqrt(i))
                sleep(1)

            if yield_id_list.check(yield_id):
                print("closed-1")
                yield_id_list.remove(yield_id)
            else:
                print("closed-2")
                return
        finally:
            print("stream_sqrt_id_data-finally")

    return generate()


@action("stream_sqrt_id", method=["GET", "POST"])
@action.uses(
    "stream_sqrt_id.html",
    db,
    session,
    auth,
    T,
    CORS(),
)
# https://stackoverflow.com/questions/31948285/display-data-streamed-from-a-flask-view-as-it-updates/31951077#31951077
def stream_sqrt_id():
    stream_url = URL("stream_sqrt_id_data")
    menu_url = URL("index")
    post_url = URL("sqrt_id_post")
    return locals()


# ------------------- task 2 : read file  ------------------------------------

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
@action.uses(
    "stream_log.html",
    db,
    session,
    auth,
    T,
    CORS(),
)
# https://stackoverflow.com/questions/31948285/display-data-streamed-from-a-flask-view-as-it-updates/31951077#31951077
def stream_log():
    stream_url = URL("stream_log_data")
    return locals()


# --------------------------------------------------------------

# LOG_FILE = 'app.log'
# log = logging.getLogger('__name__')
# logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG)

# ------------------------ task 3:  flask-sse-no-deps  -----------------------
# https://maxhalford.github.io/blog/flask-sse-no-deps/


import queue


class MessageAnnouncer:
    def __init__(self):
        self.listeners = []
        self.lock = threading.Lock()

    def listen(self):
        q = queue.Queue(maxsize=5)
        with self.lock:
            self.listeners.append(q)
        return q

    def announce(self, msg):
        with self.lock:
            for i in reversed(range(len(self.listeners))):
                try:
                    self.listeners[i].put_nowait(msg)
                except queue.Full:
                    del self.listeners[i]


announcer = MessageAnnouncer()


def format_sse(data: str, event=None) -> str:
    msg = f"data: {data}\n\n"
    if event is not None:
        msg = f"event: {event}\n{msg}"
    return msg


# 2 connect with ./sse-emit-ping.py
@action("ping", method=["GET", "POST"])
def ping():

    now = datetime.now().strftime("%H:%M:%S")
    msg = format_sse(data=f"pong {now}")
    announcer.announce(msg=msg)
    response.status = 200
    return ""


# 1 connect with ./sse-listen.py
@action("listen", method=["GET", "POST"])
def listen():
    @threadsafe_generator
    def generate():
        messages = announcer.listen()  # returns a queue.Queue
        while True:
            msg = messages.get()  # blocks until a new message arrives
            response.headers["Content-Type"] = "text/event-stream"
            yield msg

    return generate()


# -------------------------- task 4:   sse chat   ------------------------------------------
# https://github.com/jakubroztocil/chat/blob/master/app.py
# https://stackoverflow.com/questions/12232304/how-to-implement-server-push-in-flask-framework


red = redis.StrictRedis()


@threadsafe_generator
def sse_chat_event_stream():
    pubsub = red.pubsub()
    pubsub.subscribe("sse_chat_chat")
    # TODO: handle client disconnection.
    for message in pubsub.listen():
        if message["type"] == "message":
            response.headers["Content-Type"] = "text/event-stream"
            yield "data: %s\n\n" % message["data"].decode("utf-8")


# -----------------------------------------------------------


@action("sqrt_id_post", method=["POST"])
@action.uses(session)
def sqrt_id_post():

    try:
        json_data = json.loads(request.body.read())
        yield_id = json_data.get("yield_id")
        if yield_id:
            if yield_id_list.check(json_data["yield_id"]):
                print("found!  ", json_data)
                yield_id_list.remove(yield_id)
            else:
                print("not found!  ", json_data["yield_id"])

    except Exception as ex:
        print("ex! sio_chan_post: ", ex)
        print(sys.exc_info())
        return "bad"
    return "ok"


# -----------------------------------------------------------

# https://stackoverflow.com/questions/18383008/python-flask-how-to-detect-a-sse-client-disconnect-from-front-end-javascript
# https://stackoverflow.com/questions/11597367/how-do-i-close-a-server-send-events-connection-in-flask


# exception does not work !!!
@threadsafe_generator
def closed_sse_chat_event_stream():
    try:
        pubsub = red.pubsub()
        pubsub.subscribe("sse_chat_chat")

        yield_id = uuid.uuid4()
        yield_id_list.append(yield_id)

        # print(yield_id)

        # for message in pubsub.listen():#This doesn't work because it's blocking
        while True:

            if not yield_id_list.check(yield_id):
                break

            message = pubsub.get_message()

            if not message:
                # The yield is necessary for this to work!
                # In my case I always send JSON encoded data
                # An empty response might work, too.
                response.headers["Content-Type"] = "text/event-stream"
                yield "data: {}\n\n"
                sleep(0.3)
                continue

            # If the nonblocking get_message() returned something, proceed normally
            if message["type"] == "message":
                response.headers["Content-Type"] = "text/event-stream"
                yield "data: %s\n\n" % message["data"].decode("utf-8")

    finally:
        print("chat-finally")


@action( "sse_chat_stream", method=[ "GET", "POST"],)
@action.uses(session, CORS())
def sse_chat_stream():
    return closed_sse_chat_event_stream()
    #return sse_chat_event_stream()


@action("sse_chat_login", method=["GET", "POST"])
@action.uses(session, CORS())
def sse_chat_login():
    if request.method == "POST":
        session["sse_chat_user"] = request.forms.get("sse_chat_user")
        redirect(URL("sse_chat_home"))

    return (
        '<form method="get" action="%(url_index)s">'
        '    <input type="submit" value="menu">'
        "</form>"
        '<form action="" method="post">'
        'user_name: <input name="sse_chat_user">'
        '<input type="submit" value="login">'
        "</form>" % {"url_index": URL("index")}
    )


@action("sse_chat_post", method=["POST"])
@action.uses(session, CORS())
def sse_chat_post():

    message = request.forms.get("message")
    user = session.get("sse_chat_user", "anonymous")
    now = datetime.now().replace(microsecond=0).time()
    red.publish("sse_chat_chat", "[%s] %s: %s" % (now.isoformat(), user, message))
    response.status = 204
    # return "204_response"  # flask.Response(status=204)


#  204 No Content, the client doesn't need to navigate away from its current page.


@action("sse_chat_home", method=["GET", "POST"])
@action.uses(session, CORS())
def sse_chat_home():
    sse_chat_user = session.get("sse_chat_user")
    if sse_chat_user is None:
        redirect(URL("sse_chat_login"))
    return """
        <!doctype html>
        <title>sse_chat</title>
        <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js"></script>
        <style>body { max-width: 500px; margin: auto; padding: 1em; background: black; color: #fff; font: 16px/1.6 menlo, monospace; }</style>

         <style>form { display: inline-block; //Or display: inline; 
         }</style> 
 
         <form method="get" action="%(url_index)s">
             <input type="submit" value="menu">
         </form>

         <form method="get" action="%(url_user_clear)s">
             <input type="submit" value="del user">
         </form>

<script>
    function getURL() {
        window.open(  window.location.href  );
    }
</script>


<button type="button" onclick="getURL();">new tab</button>


        <p><b>hi, %(chat_user)s!</b></p>
        <p>Message: <input id="in" /></p>
        <pre id="out"></pre>
        <script>
            function sse() {
                const source = new EventSource('%(url_sse_chat_stream)s');
                const out = document.getElementById('out');
                source.onmessage = function(e) {
                    // XSS in chat is fun (let's prevent that)
                    if ( e.data != '{}' ) {
                         out.textContent =  e.data + '\\n' + out.textContent;
                    }
                };

//window.addEventListener("unload", function(event) {  source.close(); source = null; });


//document.addEventListener("visibilitychange", function() {
//    if (document.hidden){
//        console.log("Browser tab is hidden")
//        source.close();
//    } else {
//        console.log("Browser tab is visible")
//    }
//});

            }
            $('#in').keyup(function(e){
                if (e.keyCode == 13) {
                    $.post('%(url_sse_chat_post)s', {'message': $(this).val()});
                    $(this).val('');
                }
            });
            sse();
        </script>
    """ % {
        "url_index": URL("index"),
        "url_user_clear": URL("sse_chat_user_clear"),
        "url_sse_chat_stream": URL("sse_chat_stream"),
        "url_sse_chat_post": URL("sse_chat_post"),
        "chat_user": sse_chat_user,
    }


@action("sse_chat_user_clear")
@action.uses(session, CORS())
def sse_chat_user_clear():
    # session.clear()
    session["sse_chat_user"] = None
    redirect(URL("sse_chat_home"))


# ---------- this task does not work, need fix! ----------------  task 5: publisher
# https://github.com/boppreh/server-sent-events
# bottle https://taoofmac.com/space/blog/2014/11/16/1940
#


from .sseQueue import Publisher

publisher = Publisher()

# print ( publisher  )

# @app.route('/subscribe')
@action("pubsub_subscribe", method=["GET", "POST"])
@action.uses(session, CORS())
def pubsub_subscribe():
    #    #return flask.Response(publisher.subscribe(), content_type='text/event-stream')
    response.headers["Content-Type"] = "text/event-stream"
    return publisher.subscribe()


# @app.route('/')
@action("pubsub_root", method=["GET", "POST"])
@action.uses(session, CORS())
def pubsub_root():
    ip = request.environ.get("HTTP_X_FORWARDED_FOR") or request.environ.get(
        "REMOTE_ADDR"
    )  # ip = flask.request.remote_addr
    publisher.publish("New visit from {} at {}!".format(ip, datetime.now()))
    return """
<!doctype html>
<title>pubsub</title>
<html>
    <body>
        Open this page in new tabs to see the real time visits.

        <div id="events"></div>

        <script>
            const eventSource = new EventSource('%(url_pubsub_subscribe)s');
            eventSource.onmessage = function(e) {
                document.getElementById('events').innerHTML += e.data + '<br>';
            }
        </script>
    </body>
</html>
""" % {
        "url_pubsub_subscribe": URL("pubsub_subscribe"),
    }


# ----------------------------------- task 6: chart -----------------------------------
# https://ron.sh/creating-real-time-charts-with-flask/


@action("chart_data", method=["GET", "POST"])
@action.uses(session, CORS())
def chart_data():
    @threadsafe_generator
    def generate_random_data():
        try:
            while True:
                json_data = json.dumps(
                    {
                        "time": datetime.now().strftime("%d.%m.%y %H:%M:%S"),
                        "value": random.random() * 100,
                    }
                )
                # print ( json_data  )
                response.headers["Content-Type"] = "text/event-stream"
                response.headers["Cache-Control"] = "no-cache"
                response.headers["X-Accel-Buffering"] = "no"
                yield f"data:{json_data}\n\n"
                sleep(1)
        finally:
            print("chart-finally")

    return generate_random_data()


@action("sse_chart", method=["GET", "POST"])
@action.uses(
    "sse_chart.html",
    db,
    session,
    auth,
    T,
    CORS(),
)
def sse_chart():
    stream_url = URL("chart_data")
    menu_url = URL("index")
    return locals()


# ------------------------------ task7:
# https://github.com/djdmorrison/flask-progress-example


@action("progress_data", method=["GET", "POST"])
# @action.uses(session, CORS())
def progress_data():
    @threadsafe_generator
    def generate():

        try:
            x = 0

            while x <= 100:

                response.headers["Content-Type"] = "text/event-stream"
                response.headers["Cache-Control"] = "no-cache"
                response.headers["X-Accel-Buffering"] = "no"
                yield "data:" + str(x) + "\n\n"
                x += 10
                sleep(0.9)

        finally:
            print("progress-finally")

    return generate()


@action("sse_progress", method=["GET", "POST"])
@action.uses(
    "sse_progress.html",
    db,
    session,
    auth,
    T,
    CORS(),
)
def sse_progress():
    progress_url = URL("progress_data")
    menu_url = URL("index")
    return locals()

