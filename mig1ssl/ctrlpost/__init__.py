from py4web import action, request, abort, response, redirect, URL
from ..settings import APP_NAME
import sys, os, random, json, uuid, string

#from ..left_menu import l_menu

# "action": ["table", ]

import socketio
import secrets

SIO_RED_PARAM='redis://', 'channel_tornadoMig'

r_mgr = socketio.RedisManager(SIO_RED_PARAM[0], channel=SIO_RED_PARAM[1],  write_only=True, )

#event2data = {
#    "js_image_resize": ["update_image", "ImaSize"],
#    "js_count": ["update_counter", "Counter"],
#    "js_sliders": ["update_sliders", "Sliders"],
#    "connect": ["conn1", "conn2"],
#}

def do_cmd(e_nm, bcast,  *args, **kwargs):
    print (f"do_cmd: event={e_nm}")
    for a in args:
       print ( a )

    for k,v in kwargs.items():
         print (f"k={k}, v={v}") 

    json_data = json.dumps({"count": kwargs["count"], "sid":kwargs["sid"]})
    r_mgr.emit("from_do_cmd", json_data, broadcast=bcast, include_self=False)     


@action("siopost123" + str(secrets.token_hex(16)) , method=["POST",])
def siopost123():
    c_name = sys._getframe().f_code.co_name

    try:
        json_data = json.loads(request.body.read())

        event_name = json_data["event_name"]
        room = json_data["room"]
        data = json_data["data"]
        bcast = json_data["bcast"]
        print (f"username: {json_data['username']}; bcast: {bcast}")

        if data:
            do_cmd(event_name, bcast,  **data)

    except Exception as ex:
        print("ex! {c_name}:", ex)
        print(sys.exc_info())
        return f"{c_name}: bad"

    return f"{c_name}: ok"

# --------------------------------------------------------

