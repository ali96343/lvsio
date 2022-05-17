from py4web import action, request, response, abort, redirect, URL
from py4web.utils.cors import CORS


import os, sys
from math import sqrt
from random import randint
from time import sleep, time
from datetime import datetime
from urllib.parse import parse_qs #,  urlparse 
import json
import threading
from ..genhelpers  import threadsafe_generator, freturn

from itertools import count
generator_num = count(start=0, step = 1)

# For all browsers -  each domain gets a limited amount of connections 
# and the limits are global for your whole application.  4-7 connections for firefox

# https://ably.com/docs/ltask?__hsfp=952507618&__hssc=12655464.2.1646870400151&__hstc=12655464.6fa385653ecd7c9674ba06f08984886d.1646870400148.1646870400149.1646870400150.1


#red = redis.StrictRedis()
from redis import StrictRedis
#red = StrictRedis()

red = StrictRedis('localhost', 6379, charset="utf-8", decode_responses=True)

CHAN_SUF= 'generate_ltask_data'

def pub_mess(msg='hello',id_str='XXX',from_= "func"):
        RED_CHAN='monit'

        data = {
            "msg": msg,
            "from": from_,
            'id': id_str,
            "time":  datetime.now().strftime("%H:%M:%S.%f")[:-3],
            'now': datetime.now().replace(microsecond=0).time().isoformat(),
            "to": "monitor",
        }
        red.publish(RED_CHAN , json.dumps(data))

# https://stackoverflow.com/questions/21975228/redis-python-how-to-delete-all-keys-according-to-a-specific-pattern-in-python

# reconnect about
# https://stackoverflow.com/questions/24564030/is-an-eventsource-ltask-supposed-to-try-to-reconnect-indefinitely

#  curl http://localhost:8000/ssep4w/ltask/ltask_data
# https://matthewminer.com/2015/02/21/pattern-for-async-task-queue-results

@action("ltask/ltask_data", )
def ltask_data():


    lastId = request.GET.get('lastId', 0 )

    try:
        lastId = int(lastId)
    except Exception as ex:
        ex_template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        ex_msg = ex_template.format(type(ex).__name__, ex.args)
        print (ex_msg)
        lastId = 0


    @threadsafe_generator
    def generate_ltask_data():
        try:
            gen_id = str(next(generator_num) )

            red_chan= f"{gen_id}_{CHAN_SUF}"
            pubsub = red.pubsub()
            pubsub.subscribe( [ red_chan, red_chan + '_cel'  ] )

            start_flag = True
            last_event = lastId + 1

            msg_str = ''
            ltask_result='' #'here ltask_result'
            while True:
                message = pubsub.get_message()
                #if message:
                #     print (message)

                
                if message and message['type'] == 'message':
                    if message['channel'] == red_chan:
                        msg_str = message['data']
                    if message['channel'] == red_chan+ '_cel':
                        ltask_result = message['data']
                        
                json_data = json.dumps(
                    {
                        "time": datetime.now().strftime("%H:%M:%S.%f")[:-3],
                        "value": randint(0,100),
                        'gen_id': gen_id,
                        "red_chan": red_chan,
                        "msg_str": msg_str,
                        "ltask": ltask_result,
                    }
                )


                if start_flag:
                    yield f"event: generator_start\ndata:{json_data}\n\n"
                    start_flag = False
                    
                yield f"data:{json_data}\nid: {last_event}\n\n"
                sleep(0.5)
                last_event +=  1

        except Exception as ex:
            ex_template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            ex_msg = ex_template.format(type(ex).__name__, ex.args)
            print (ex_msg)


        finally:
            pubsub.unsubscribe([ red_chan, red_chan + '_cel'  ])
            print ( f"finally: {sys._getframe().f_code.co_name}; id: {gen_id}" )
            message = 'stop' + ' ' + gen_id 
#            pub_mess( msg='stop', id_str=gen_id, from_= user  )

    response.headers["Content-Type"] = "text/event-stream"
    response.headers["Cache-Control"] = "no-cache" 
    return generate_ltask_data()

# mymap = r_server.keys(pattern='example.*')


@action("ltask/ltask", )
@action.uses( "ltask/ltask.html", )
def ltask():
    hint1_url=URL('ltask/get_hint1_data')
    stream_url = URL("ltask/ltask_data") 
    ltask_url = URL ('ltask/runltask')
    return locals()


# ----------------------------------------------------------------------------
# https://matthewminer.com/2015/02/21/pattern-for-async-task-queue-results

# redis-cli subscribe '0_generate_ltask_data'

@action('ltask/get_hint1_data')
@action.uses(CORS())
def get_hint1_data():
    q = request.GET.get('q', '' )
    g = request.GET.get('generatorId','')
    red.publish( f"{g}_{CHAN_SUF}", f"{q}" )
    return f'{q}'

from ..ltask_worker import longtask_mytask 

@action('ltask/runltask', method=['POST'])
#@action.uses(CORS())
def runltask():
    generatorId = request.forms.get('generatorId')
    #print ( '+++++++++ ',f"{generatorId}_{CHAN_SUF}"  )
    clientid = f"{generatorId}_{CHAN_SUF}_cel"  
    red.publish( clientid , "wait... did you run ltask_worker.sh ?" )
    longtask_mytask.delay(clientid=clientid)
    #response.status = 202
    #return 'running task...wait ans over redis' #, 202
    return freturn( 'running task...wait ans over redis' , 202 )


@action("ltask/longtask_notify", method=["POST",])
def longtask_notify():

    def to_str( b  ):
       return b.decode("utf-8")


    try:
       body = parse_qs( request.body.read() )
       clientid =  to_str( body[b'clientid'][0]   )
       result = to_str( body[b'result'][0] )
       result_str = f'{result}, clientid: {clientid}'
       #print ('??????????? ', clientid, '  ', result_str)
       red.publish( f"{clientid}", f"{result_str}" )

    except Exception as ex:
       ex_template = "An exception of type {0} occurred. Arguments:\n{1!r}"
       ex_msg = ex_template.format(type(ex).__name__, ex.args)
       print (ex_msg)


