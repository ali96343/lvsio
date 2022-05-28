from py4web import action, request, response, abort, redirect, URL
import os, sys

from math import sqrt
from time import sleep
from datetime import datetime
import json
import threading
import uuid
from itertools import count

unique_num = count(start=0, step = 1) 


class SafeList:
    def __init__(self):
        self._list = list()
        self._lock = threading.Lock()

    def append(self, value):
        with self._lock:
            self._list.append(value)

    def check(self, value):
        with self._lock:
            return value in self._list

    def remove(self, value):
        with self._lock:
            self._list.remove(value)

    def pop(self):
        with self._lock:
            return self._list.pop()

    def get(self, index):
        with self._lock:
            return self._list[index]

    def length(self):
        with self._lock:
            return len(self._list)

yield_id_list = SafeList()

# ---------------------------------------------------------------------------

# https://gist.github.com/platdrag/e755f3947552804c42633a99ffd325d4

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
# ------------------------------------------------------------------------

def threads_info():
    print ( f"========== {sys._getframe().f_code.co_name}" )

    #print (sys._current_frames().values() )
    f = list(sys._current_frames().values())[0]
    print ("    ",f.f_back.f_globals['__file__'] )
    print ("    ", f.f_back.f_globals['__name__'] )
    getframe_expr = "sys._getframe({}).f_code.co_name"
    caller = eval(getframe_expr.format(2))
    callers_caller = eval(getframe_expr.format(3))
    print(" --  called from: ", caller)
    print("    ", caller, "was called from: ", callers_caller, "--")

    print("     name:  ",threading.current_thread().name)
    print("     ident: ",threading.get_ident())
    _ = [     print('           ',thread.name) for thread in threading.enumerate() ]

# ------------------------------------------------------------------------

@action("polling/stream_sqrt_id_data", method=["GET", ])
def stream_sqrt_id_data():

    gen_id = str(next(unique_num) )
    @threadsafe_generator
    def generate_sqrt():

        #threads_info()

        try:

            yield_id = str(uuid.uuid4())
            yield_id_list.append(yield_id)

            for i in range(30):

                if not yield_id_list.check(yield_id):
                    break

                json_data = json.dumps(
                    {
                        "time": datetime.now().strftime("%H:%M:%S.%f")[:-3], 
                        "value": f"{sqrt(i):.2f}",
                        "yield_id": yield_id,
                        'gen_id': gen_id,
                    }
                )

                response.headers["Cache-Control"] = "no-store"
                yield f"{json_data}\n\n"
                sleep(1)

        finally:
            if yield_id_list.check(yield_id):
                yield_id_list.remove(yield_id)
            print ( f"finally: {sys._getframe().f_code.co_name}; id: {gen_id}" )

    return generate_sqrt()

@action("polling/sqrt_id_post", method=["POST"])
def sqrt_id_post():

    try:
        json_data = json.loads(request.body.read())
        yield_id = json_data.get("yield_id")
        if yield_id_list.check(json_data["yield_id"]):
            yield_id_list.remove(yield_id)
        #    print("found: ", json_data)
        #else:
        #    print("not found: ", json_data)

    except Exception as ex:
        print(f"ex! {sys._getframe().f_code.co_name}: ", ex)
        print(sys.exc_info())
        #template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        #message = template.format(type(ex).__name__, ex.args)
        #print (message)

@action("polling/stream_sqrt_id", method=["GET", ])
@action.uses( "polling/stream_sqrt_id.html", )
def stream_sqrt_id():
    return dict( stream_url = URL("polling/stream_sqrt_id_data"),
                 post_url = URL("polling/sqrt_id_post") )
