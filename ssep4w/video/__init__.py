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

from ..genhelpers import func_timer_decorator, threadsafe_generator
#from ..base import *



# stream_time -------------------------------------------------------------
@action("video/jpeg_stream_data", method=["GET", ])
@func_timer_decorator
def jpeg_stream_data():

    camera = Camera()

    gen_id = str(next(generator_num) )
    @threadsafe_generator
    def generate_frames():
        try:

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
