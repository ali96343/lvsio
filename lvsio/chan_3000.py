#!/usr/bin/env python3
import sys, os
# sys.path.insert(0, '')

import uvicorn
import socketio
import httpx
import requests

# pip install aioredis==1.3.1

# gevent-socket io https://bravenewgeek.com/real-time-client-notifications-using-redis-and-socket-io/
# https://stackoverflow.com/questions/52596096/flask-socketio-redis-subscribe


# --------------- global ------------------------------------------

sio_debug = True

values = {
    "slider1": 25,
    "slider2": 0,
    "counter": 100, # to be continued
    "data_str": ":)",
}

PORT = 3000
HOST = '127.0.0.1'
SERV_APP_FILE = "chan_3000:app"

this_dir = os.path.dirname( os.path.abspath(__file__) )
#if not this_dir in sys.path:
#    sys.path.insert(0,  this_dir )

P4W_APP =  this_dir.split(os.sep)[-1]

print ( '+++++++++++ ', P4W_APP )




sio_debug and print(f"===: {SERV_APP_FILE}")
post_url = f"http://127.0.0.1:8000/{P4W_APP}/from_uvicorn"
BROADCAST_SECRET = "123secret"

# ----------------------------------------------------------------
r_url = "redis://"
r_mgr = socketio.AsyncRedisManager(r_url, write_only=False)
sio = socketio.AsyncServer(
    async_mode="asgi",
    client_manager=r_mgr,
    cors_allowed_origins="*",
    SameSite=None,
    logger=True,
    engineio_logger=True,
)
app = socketio.ASGIApp(sio, static_files={"/": "./public/index.html"})

# --------------------------- utils ----------------------------------------------

# https://pypi.org/project/stirfried/

# https://zetcode.com/python/httpx/


async def XXXsio_event_post(event_name, data=None, room=None, post=True):
    global BROADCAST_SECRET
    global post_url

    json_data = {
        "event_name": event_name,
        "data": data,
        "room": room,
        "broadcast_secret": BROADCAST_SECRET,
    }

    x = requests.post(post_url, json=json_data)

    if x.status_code != 200:
        print(f"error! can not post to: {post_url}")


async def sio_event_post(event_name, data=None, room=None, post=True):

    # https://zetcode.com/python/httpx/

    global BROADCAST_SECRET
    global post_url 

    json_data = {
        "event_name": event_name,
        "data": data,
        "room": room,
        "broadcast_secret": BROADCAST_SECRET,
    }

    async with httpx.AsyncClient() as client:
        r = await client.post(post_url, json=json_data)

        if r.status_code != 200:
            print(f"error! can not post to: {post_url}")

#---------------------------------------------------------------------------

@sio.event
async def connect(sid, environ):
    sio_debug and print(sid, "connected")


@sio.event
async def disconnect(sid):
    sio_debug and print(sid, "disconnected")


#-----  events for page sync_id.html ---------------------------------------

@sio.event
async def sync_hello_connect(sid, data):
    sio_debug and print(data)


@sio.event
async def counter_changed(sid, data):
    sio_debug and print(data)
    # await sio.emit('update_value', data, broadcast=True, include_self=False)


@sio.event
async def values_save(sid, data):
    sio_debug and print(data)


@sio.on("value_changed")
async def value_changed(sid, message):
    sio_debug and print(message)
    global values
    values[message["who"]] = message["data"]
    await sio_event_post("sample-event", data="emit-data", room="some_room")
    await sio.emit("update_value", message, broadcast=True, include_self=False)
    # await server.emit('update_value', message, broadcast=True, include_self=False)


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
        app=SERV_APP_FILE,
        host=HOST,
        port=PORT,
        reload=True,
        workers=1,
        debug=False,
    )
