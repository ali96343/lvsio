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

from random import randint
from PIL import Image
from io import BytesIO
from copy import deepcopy


class Camera(object):

    def __init__(self):
        self.this_dir = os.path.dirname(os.path.abspath(__file__))
        self.jpeg_list = [ os.path.join(self.this_dir, f + ".jpg") for f in ['1', '2', '3'] ]
        self.frames = [open(f , 'rb').read() for f in self.jpeg_list   ]
        self.lock = threading.Lock()
        with self.lock :
            self.colorize_jpeg()


    def colorize_jpeg(self,):

        colors=('green', 'pink', 'orange', 'coral', 'cyan','purple','yellow', 'violet', 'navy')
        b_color = colors [ randint(0, len(colors )-1) ]
        right =  left =  top =  bottom = 7

        for i, curimg in enumerate(self.frames):
            in_buff = BytesIO()
            out_buff = BytesIO()
            in_buff.write(curimg)
            in_buff.seek(0) #need to jump back to the beginning before handing it off to PIL

            ima = Image.open(in_buff)
  
            w, h = ima.size
  
            result = Image.new(ima.mode, (w + right + left ,h + top + bottom), b_color )
            result.paste(ima, (left, top))
      
            out_buff.seek(0) #need to jump back to the beginning before handing it off to PIL
            result.save(out_buff , format='JPEG')
            self.frames[i] = out_buff.getvalue() 
            #self.frames[i] = deepcopy(out_buff.getvalue() )
              

    def get_frame(self):
        with self.lock:
            return self.frames[int(time()) % 3]

# -------------------------------------------------------------------------

# ./py4web.py run apps --watch=off -s wsgirefThreadingServer

# ---------------------------------------------------------------------------

from ..genhelpers import func_timer_decorator, threadsafe_generator


# stream_time -------------------------------------------------------------
@action("video/jpeg_stream_data", )
#@func_timer_decorator
def jpeg_stream_data():

    camera = Camera()

    gen_id = str(next(generator_num) )
    @threadsafe_generator
    def generate_frames():
        try:
            while True:

                response.headers["Content-Type"]= 'multipart/x-mixed-replace; boundary=frame'
                yield (b'--frame\r\n'
                     b'Content-Type: image/jpeg\r\n\r\n' + camera.get_frame() + b'\r\n')
                sleep(1)

        except Exception as ex:
            print (f"{sys._getframe().f_code.co_name}: An exception of type {type(ex).__name__} occurred. Arguments: {ex.args}"  )

        finally:
           print ( f"finally: {sys._getframe().f_code.co_name}; id: {gen_id}" )

    return generate_frames()


@action("video/jpeg_stream", )
@action.uses( "video/jpeg_stream.html", )
def jpeg_stream():
    return dict(stream_url = URL("video/jpeg_stream_data") )
