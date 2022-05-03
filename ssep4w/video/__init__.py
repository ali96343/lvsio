from py4web import action, request, response, abort, redirect, URL
from py4web.utils.cors import CORS


import os, sys
from math import sqrt
from time import sleep, time
from datetime import datetime
import json
import threading
from contextlib import contextmanager

from itertools import count
generator_num = count(start=0, step = 1)

# git clone https://github.com/miguelgrinberg/flask-video-streaming.git




class Camera(object):
    def __init__(self):
        self.this_dir = os.path.dirname(os.path.abspath(__file__))
        self.jpeg_list = [ os.path.join(self.this_dir, f + ".jpg") for f in ['1', '2', '3'] ]
        self.frames = [open(f , 'rb').read() for f in self.jpeg_list   ]
        self.lock = threading.Lock()

    def get_frame(self):
        with self.lock:
            return self.frames[int(time()) % 3]


# -------------------------------------------------------------------------

# ./py4web.py run apps --watch=off -s wsgirefThreadingServer

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



# stream_time -------------------------------------------------------------

@action("video/jpeg_stream_data", method=["GET", ])
def jpeg_stream_data():

    # ./py4web.py run apps --watch=off -s wsgirefThreadingServer
    camera = Camera()

    @threadsafe_generator
    def generate_frames():
        try:

            gen_id = str(next(generator_num) )
            while True:



                frame = camera.get_frame()
                response.headers["Content-Type"]= 'multipart/x-mixed-replace; boundary=frame'
                yield (b'--frame\r\n'
                     b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                sleep(1)

        except Exception as ex:
            ex_template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            ex_msg = ex_template.format(type(ex).__name__, ex.args)
            print (ex_msg)

        finally:
           print ( f"finally: {sys._getframe().f_code.co_name}; id: {gen_id}" )

    return generate_frames()


@action("video/jpeg_stream", method=["GET", ])
@action.uses( "video/jpeg_stream.html", )
def jpeg_stream():
    return dict(stream_url = URL("video/jpeg_stream_data") )
