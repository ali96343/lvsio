
from py4web import action, request, response, abort, redirect, URL
from py4web.utils.cors import CORS


import os, sys
from math import sqrt
from random import randint
from time import sleep, time
from datetime import datetime
import json
import threading

from itertools import count

generator_num = count(start=0, step=1)




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


# red = redis.StrictRedis()
from redis import StrictRedis

red = StrictRedis()

RED_CHAN = "monit"


def clear_red_ns(ns):
    """
    Clears a namespace in redis cache.
    This may be very time consuming.
    :param ns: str, namespace i.e your:prefix*
    :return: int, num cleared keys
    """
    count = 0
    pipe = cache.pipeline()
    for key in red.scan_iter(ns):
        pipe.delete(key)
        count += 1
    pipe.execute()
    return count


# https://stackoverflow.com/questions/21975228/redis-python-how-to-delete-all-keys-according-to-a-specific-pattern-in-python


# stream_time -------------------------------------------------------------

this_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(this_dir, "flog.log")


@action( "flog/flog_data", method=[ "GET", ],)
def flog_data():
   # print (request.GET.get('lastId', ) )

    try:
        lastId = request.GET.get('lastId', 0 )
        lastId = int(lastId)
    except Exception as ex:
        ex_template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        ex_msg = ex_template.format(type(ex).__name__, ex.args)
        print (ex_msg)
        lastId = 0

    #print ( lastId)




    # pubsub = red.pubsub()
    # pubsub.subscribe( RED_CHAN )

    def pub_mess(msg="hello", id_str="XXX", from_="func"):

        data = {
            "msg": msg,
            "from": from_,
            "id": id_str,
            "time": datetime.now().strftime("%H:%M:%S.%f")[:-3],
            "now": datetime.now().replace(microsecond=0).time().isoformat(),
            "to": "monitor",
        }
        red.publish(RED_CHAN, json.dumps(data))

    gen_id = str(next(generator_num))
    @threadsafe_generator
    def generate_flog_data():
        try:

            user = sys._getframe().f_code.co_name

            #            pub_mess( msg='start', id_str=gen_id, from_= user  )

            start_flag = True
            event_id = lastId + 1 

            with open(file_path, 'r') as f:


# https://stackoverflow.com/questions/13456735/how-to-wrap-a-python-iterator-to-make-it-thread-safe
#def locked_iter(it):
#    it = iter(it)
#    lock = threading.Lock()
#    while True:
#        try:
#            with lock:
#                value = next(it)
#        except StopIteration:
#            return
#        yield value

                _flock = threading.Lock()
                for _ in range(lastId): 
                     with  _flock:
                          next(f)
                
                while True:


                    line = f.readline()

                    if not line : #or not line.endswith("\n"):
                        sleep(0.5)
                        continue

                    json_data = json.dumps(
                        {
                            "time": datetime.now().strftime("%H:%M:%S.%f")[:-3],
                            "value": randint(0, 100),
                            "gen_id": gen_id,
                        }
                    )

                    response.headers["Content-Type"] = "text/event-stream"
                    response.headers["Cache-Control"] = "no-cache"
                    response.headers["X-Accel-Buffering"] = "no"

                    if start_flag:
                        yield f"event: generator_start\ndata:{json_data}\n\n"
                        start_flag = False

                    yield f"id: {event_id}\ndata: {line}\n\n"
                    #yield f"data: {line}\ndata::{json_data}\nid: {lastId}\n\n"
                    sleep(1)
                    event_id += 1

        except Exception as ex:
            ex_template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            ex_msg = ex_template.format(type(ex).__name__, ex.args)
            print (ex_msg)
        
        finally:
            print(f"finally: {sys._getframe().f_code.co_name}; id: {gen_id}")
            message = "stop" + " " + gen_id
            #pub_mess(msg="stop", id_str=gen_id, from_=user)

    return generate_flog_data()


# mymap = r_server.keys(pattern='example.*')


@action( "flog/flog", method=[ "GET", ],)
@action.uses( "flog/flog.html",)
def flog():
    return dict(stream_url=URL("flog/flog_data"))
