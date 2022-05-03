from py4web import action, request, response, abort, redirect, URL

import os, sys
from time import sleep, time
import threading

from itertools import count

generator_num = count(start=0, step=1)

# -------------------------------------------------------------------------

# ./py4web.py run apps --watch=off -s wsgirefThreadingServer


# -------------------------------- UTILS ------------------

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



# -------------------------------  task ---------------------------------------

this_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(this_dir, "video.webm")

@action( "webm/webm_stream_data", method=[ "GET", ],)
def webm_stream_data():

    CHUNK = 20 * 1024
    if not os.path.isfile(file_path):
        raise RuntimeError(f"Could not open {file_path}.")
  
    @threadsafe_generator 
    def generate_webm(): 
        try:
            gen_id = str(next(generator_num) )
    
            with open(file_path, "rb") as f:

                filesize = os.path.getsize(file_path)
    
                start, end  = 0, CHUNK

                fs = 0

                while filesize : #True:
                    f.seek(start)
                    data = f.read(CHUNK)

                    fs += len(data)
    
                    response.headers[
                        "Content-Range"
                    ] = f"bytes {str(start)}-{str(end)}/{str(filesize)}"
                    response.headers["Accept-Ranges"] = "bytes"
                    response.headers["Content-Type"] = "video/webm"
                    response.status = 206
    
                    yield data

                    if len(data) < CHUNK:
                        break
    
                    start = end; end += CHUNK

                    sleep(0.05)

        except Exception as ex:
            ex_template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            ex_msg = ex_template.format(type(ex).__name__, ex.args)
            print (ex_msg)

        finally:
            print ( f"finally: {sys._getframe().f_code.co_name}; id: {gen_id}," 
                    f"file-size: {fs} bytes" )
            if filesize != fs:
                  (print ('file-size error: {filesize} vs  {fs}'))
    
    return generate_webm()


@action( "webm/webm_stream", method=[ "GET", ],)
@action.uses( "webm/webm_stream.html",)
def webm_stream():
    return dict(stream_url=URL("webm/webm_stream_data"))

