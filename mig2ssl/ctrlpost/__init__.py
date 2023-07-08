from py4web import action, request, abort, response, redirect, URL
from ..settings import APP_NAME
import sys, os, random, json, uuid, string

from ..left_menu import l_menu

# "action": ["table", ]

import secrets

SIO_POST_SECRET = str(secrets.token_hex(32)) 

sio_chan = "channel_tornadoMig"

event2data = {
    "js_image_resize": ["update_image", "ImaSize"],
    "js_count": ["update_counter", "Counter"],
    "js_sliders": ["update_sliders", "Sliders"],
    "connect": ["conn1", "conn2"],
}

def do_event(*args, **kwargs):
    tbl = kwargs["t_name"]  #'Counter'

    #flds = [e for e in db[tbl].fields if e != "id"]
    #ftypes = [db[tbl][e].type for e in flds]
    print (tbl)



@action("siopost123", method=["POST",])
#@action.uses()
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


    except Exception as ex:
        print("ex! siopost123: ", ex)
        print(sys.exc_info())
        return f"{c_name}: bad"

    return f"{c_name}: ok"

# --------------------------------------------------------
