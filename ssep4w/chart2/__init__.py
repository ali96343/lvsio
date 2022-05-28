from py4web import action, request, response, abort, redirect, URL
import logging, os, sys
from py4web.utils.cors import CORS


from time import sleep
from datetime import datetime
from random import randint
import json
import threading

from itertools import count
unique_num = count(start=0, step = 1)


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


# https://stackoverflow.com/questions/61489186/browser-refresh-not-sending-the-last-event-id-received-as-part-of-server-sent-re


@action("chart2/sse_chart_data", method=["GET", ])
@action.uses( CORS())
def sse_chart_data(lastId=0):

    lastId = request.GET.get('lastId', 0 ) 

    try:
        lastId = int(lastId)
    except:
        lastId = 0 

    #print ( f'sse_chart_data: lastId {lastId}' )
    gen_id = str(next(unique_num) )

    @threadsafe_generator
    def generate_chart_data():

        try:
            
            xvalue= lastId + 1
            event_id = lastId + 1 
            while True:

                json_data = json.dumps(
                    {
                        'x' : xvalue, 
                        "y": randint( 10, 90), 
                        "time": datetime.now().strftime("%H:%M:%S.%f")[:-3],
                        'gen_id': gen_id,
                    }
                )

                response.headers["Cache-Control"] = "no-cache"
                response.headers["Content-Type"] = "text/event-stream"
                response.headers["X-Accel-Buffering"] = "no"
                yield f"data:{json_data}\nid: {event_id}\n\n"
                sleep(1)
                xvalue += 1
                event_id += 1

        except Exception as ex:
            ex_template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            ex_msg = ex_template.format(type(ex).__name__, ex.args)
            print (ex_msg)

        finally:
            print ( f"finally: {sys._getframe().f_code.co_name}; id: {gen_id}" ) 

    return generate_chart_data()


@action("chart2/sse_chart", method=["GET", ])
@action.uses( "chart2/chart.html" )
def sse_chart():
    stream_url = URL("chart2/sse_chart_data")
    return locals()

