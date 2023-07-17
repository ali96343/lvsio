from py4web import action, request, abort, response, redirect, URL
from ..settings import APP_NAME
import sys, os, random, json, uuid, string

#from ..left_menu import l_menu

# "action": ["table", ]

import socketio
import secrets

SIO_RED_PARAM='redis://', 'channel_tornadoMig'

r_mgr = socketio.RedisManager(SIO_RED_PARAM[0], write_only=True, channel=SIO_RED_PARAM[1] )
#r_mgr = socketio.RedisManager("redis://", write_only=True, channel="channel_tornadoMig" )


#event2data = {
#    "js_image_resize": ["update_image", "ImaSize"],
#    "js_count": ["update_counter", "Counter"],
#    "js_sliders": ["update_sliders", "Sliders"],
#    "connect": ["conn1", "conn2"],
#}

def do_cmd(e_nm, *args, **kwargs):
    print (f"do_cmd: {e_nm}")
    for a in args:
       print ( a )

    for k,v in kwargs.items():
         print ("%s = %s" % (k, v) )

    json_data = json.dumps({"count": kwargs["count"], "sid":kwargs["sid"]})
    r_mgr.emit("from_do_cmd", json_data, broadcast=True, include_self=False)     


@action("siopost123" + str(secrets.token_hex(16)) , method=["POST",])
def siopost123():

    c_name = sys._getframe().f_code.co_name

    try:
        json_data = json.loads(request.body.read())

        event_name = json_data["event_name"]
        room = json_data["room"]
        data = json_data["data"]
        print ("username:",request.headers.get('username',))

        if data:
            #print (data)
            do_cmd(event_name, **data)


    except Exception as ex:
        print("ex! {c_name}:", ex)
        print(sys.exc_info())
        return f"{c_name}: bad"

    return f"{c_name}: ok"

# --------------------------------------------------------
