from py4web import action, request, response, abort, redirect, URL
from py4web.utils.cors import CORS


import os, sys
from math import sqrt
from random import randint
from time import sleep, time
from datetime import datetime
import json
import threading
from ..genhelpers  import threadsafe_generator 

from itertools import count
generator_num = count(start=0, step = 1)

# For all browsers -  each domain gets a limited amount of connections 
# and the limits are global for your whole application.  4-7 connections for firefox

# https://ably.com/docs/sse?__hsfp=952507618&__hssc=12655464.2.1646870400151&__hstc=12655464.6fa385653ecd7c9674ba06f08984886d.1646870400148.1646870400149.1646870400150.1


#red = redis.StrictRedis()
from redis import StrictRedis
red = StrictRedis()
RED_CHAN='monit'

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

# reconnect about
# https://stackoverflow.com/questions/24564030/is-an-eventsource-sse-supposed-to-try-to-reconnect-indefinitely


# stream_time -------------------------------------------------------------

@action("sse/sse_time_data", method=["GET", ])
def sse_time_data():

    # ./py4web.py run apps --watch=off -s wsgirefThreadingServer

    # yield self.imgs[int(time.time()) % 3]

    #pubsub = red.pubsub()
    #pubsub.subscribe( RED_CHAN )

    try:
        lastId = request.GET.get('lastId', 0 )
        lastId = int(lastId)
    except Exception as ex:
        ex_template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        ex_msg = ex_template.format(type(ex).__name__, ex.args)
        print (ex_msg)
        lastId = 0

    #print ( lastId)

    def pub_mess(msg='hello',id_str='XXX',from_= "func"):

        data = {
            "msg": msg,
            "from": from_, 
            'id': id_str,
            "time":  datetime.now().strftime("%H:%M:%S.%f")[:-3], 
            'now': datetime.now().replace(microsecond=0).time().isoformat(),
            "to": "monitor",
        }
        red.publish(RED_CHAN , json.dumps(data))


    @threadsafe_generator
    def generate_time_data():
        try:
            gen_id = str(next(generator_num) )

            user = sys._getframe().f_code.co_name
    
            #pub_mess( msg='start', id_str=gen_id, from_= user  )


            red_chan= f"{gen_id}_generate_time_data"



            start_flag = True
            last_event = lastId + 1

            while True:
        
                json_data = json.dumps(
                    {
                        "time": datetime.now().strftime("%H:%M:%S.%f")[:-3],
                        "value": randint(0,100),
                        'gen_id': gen_id,
                    }
                )

                response.headers["Content-Type"] = "text/event-stream"
                response.headers["Cache-Control"] = "no-store" 

                if start_flag:
                    yield f"event: generator_start\ndata:{json_data}\n\n"
                    start_flag = False
                    
                yield f"data:{json_data}\nid: {last_event}\n\n"
                sleep(1)
                last_event +=  1

        except Exception as ex:
            ex_template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            ex_msg = ex_template.format(type(ex).__name__, ex.args)
            print (ex_msg)


        finally:
            print ( f"finally: {sys._getframe().f_code.co_name}; id: {gen_id}" )
            message = 'stop' + ' ' + gen_id 
#            pub_mess( msg='stop', id_str=gen_id, from_= user  )


    return generate_time_data()

# mymap = r_server.keys(pattern='example.*')


@action("sse/sse_time", method=["GET", ])
@action.uses( "sse/sse_time.html", )
def sse_time():
    hint1_url=URL('sse/get_hint1_data')
    stream_url = URL("sse/sse_time_data") 
    return locals()


# ----------------------------------------------------------------------------

@action('sse/get_hint1_data')
@action.uses(CORS())
def get_hint1_data():
   q = request.GET.get('q', '' )
   g = request.GET.get('generatorId','')
   red_chan= f"{g}_generate_time_data"
   #print (red_chan)
   return f'{q}'

