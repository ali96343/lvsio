#!/usr/bin/env python3
import sys, os
# sys.path.insert(0, '')

import uvicorn
import socketio
import httpx
import requests
from renoir import Renoir

# pip install aioredis==1.3.1

# gevent-socket io https://bravenewgeek.com/real-time-client-notifications-using-redis-and-socket-io/
# https://stackoverflow.com/questions/52596096/flask-socketio-redis-subscribe


# --------------- global ------------------------------------------
sio_debug = False

this_dir = os.path.dirname( os.path.abspath(__file__) )
if not this_dir in sys.path:
    sys.path.insert(0,  this_dir )

import chan_conf as C

# ----------------------------------------------------------------
r_mgr = socketio.AsyncRedisManager(C.r_url, channel=C.sio_channel,  write_only=False)
sio = socketio.AsyncServer(
    async_mode="asgi",
    client_manager=r_mgr,
    cors_allowed_origins="*",
    SameSite=None,
    logger=True,
    engineio_logger=True,
)
app = socketio.ASGIApp(sio, static_files={"/": "./chan_public/index.html"})

# --------------------------- utils ----------------------------------------------


async def sio_event_post(event_name, data=None, room=None, post=True):

    # https://zetcode.com/python/httpx/

    json_data = {
        "event_name": event_name,
        "data": data,
        "room": C.sio_room, #room,
        "broadcast_secret": C.BROADCAST_SECRET,
    }

    headers = {'X-Custom': 'value'}

    headers = {
            'app-param': C.P4W_APP,
            'content-type': "application/json",
            'cache-control': "no-cache"
    }


    async with httpx.AsyncClient() as client:
        r = await client.post(C.post_url, json=json_data, headers=headers)

        if r.status_code != 200:
            print(f"error! can not post to: {C.post_url}")


#---------------------------------------------------------------------------

@sio.event
async def connect(sid, environ):
    sio_debug and print(sid, "connected")


@sio.event
async def disconnect(sid):
    sio_debug and print(sid, "disconnected")

@sio.event
async def sync_connect(sid, data):
    sio_debug and print(data)

# ------------------------- ImaSize ------------------------------------------

@sio.event
async def js_image_resize(sid, data):
    sio_debug and print(data)
    e_name = sys._getframe().f_code.co_name
    await sio_event_post( e_name  , data=data, room="some_room")


# ---------------------------Counter------------------------------------==

@sio.event
async def js_count(sid, data):
    sio_debug and print(data)
    e_name = sys._getframe().f_code.co_name
    await sio_event_post( e_name  , data=data, room="some_room")

# ---------------------- Sliders--------------------------------------==

@sio.event
async def js_sliders(sid, data):
    sio_debug and print("sio js_sliders: ",data)
    e_name = sys._getframe().f_code.co_name
    await sio_event_post( e_name  , data=data, room="some_room")



#-----  events for page flask_chat.html ---------------------------------------


def messageReceived(methods=["GET", "POST"], ):
    sio_debug and print("message was received!!!")


@sio.on("my_event")
async def handle_my_custom_event(sid, json):
    sio_debug and print("received my_event: " + str(json))
    #await sio.emit("my_response", json, )
    await sio.emit("my_response", json, room=sid, callback=messageReceived)

# https://github.com/miguelgrinberg/python-socketio/issues/160
# https://stackoverflow.com/questions/43301977/flask-socket-io-result-of-emit-callback-is-the-response-of-my-rest-endpoint
# -----------------------------------------------------------------------------------------------


if __name__ == "__main__":
    # https://www.fatalerrors.org/a/uvicorn-a-lightweight-and-fast-python-asgi-framework.html
    # uvicorn.run(app=app, host="127.0.0.1", port=5000, log_level="info")

    uvicorn.run(
        app=C.SERV_APP_FILE,
        host=C.sio_HOST,
        port=C.sio_PORT,
        reload=True,
        # log_level='critical', # 'critical', 'error', 'warning', 'info', 'debug', 'trace'.
        workers=1,
        debug=False,
    )


