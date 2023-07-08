from py4web import action, request, abort, response, redirect, URL
from ..settings import APP_NAME
import sys, os, random, json, uuid, string

#from ..left_menu import l_menu

# "action": ["table", ]

import socketio
import secrets

SIO_POST_SECRET = str(secrets.token_hex(32)) 

r_mgr = socketio.RedisManager("redis://", write_only=True, channel="channel_tornadoMig" )

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


@action("siopost123", method=["POST",])
def siopost123():

    c_name = sys._getframe().f_code.co_name

    try:
        json_data = json.loads(request.body.read())

        if json_data["post_secret"] ==  SIO_POST_SECRET:
            print (f"ctrl_p4w {c_name}: {APP_NAME} secret ok! {SIO_POST_SECRET}")
        else:
            print (f"ctrl_p4w {c_name}: {APP_NAME} secret bad! {SIO_POST_SECRET}")
            return f"{c_name}: {APP_NAME} bad"

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
