#!/usr/bin/env python3

import uvicorn
import socketio


#--------------- global ------------------------------------------

PORT=3000
SERV_APP_FILE = "chan_3000:app"
P4W_APP='lvsio'
sio_debug = True
# ----------------------------------------------------------------

sio = socketio.AsyncServer(async_mode='asgi',  cors_allowed_origins='*', SameSite=None )
app = socketio.ASGIApp(sio, static_files={ '/': './templates/sync_id.html' })

# https://stackoverflow.com/questions/57579110/how-to-fix-access-control-allow-origin-error-in-a-python-socket-io-server
# https://stackoverflow.com/questions/52596096/flask-socketio-redis-subscribe

#--------------------------- utils ----------------------------------------------
# https://stackoverflow.com/questions/46675351/how-to-emit-events-from-celery-task
import requests

# https://pypi.org/project/stirfried/

async def sio_event_post(event_name, post_url= None,  data=None, room=None, post= True):
    BROADCAST_SECRET='123secret'
    P4W_APP = 'mig' #os.getenv('P4W_APP')
    post_url = f'http://127.0.0.1:8000/{P4W_APP}/from_uvicorn'

    json_data = {
        'event_name': event_name,
        'data': data,
        'room': room,
        'broadcast_secret': BROADCAST_SECRET 
    }

    x=requests.post(post_url, json=json_data)
    
    if x.status_code != 200:
        print (f'error! can not post to: {post_url}')
    

#--------------------------------------------------------------------------------




values = {
    'slider1': 25,
    'slider2': 0,
    'counter': 100,
    'data_str': ':)',
}

sio_debug and print (f'===: {SERV_APP_FILE}')

@sio.event
async def connect(sid, environ):
    sio_debug and print(sid, 'connected')


@sio.event
async def disconnect(sid):
    sio_debug and print(sid, 'disconnected')


@sio.event
async def sync_hello_connect(sid, data):
     sio_debug and  print (data)

@sio.event
async def counter_changed(sid, data):
     sio_debug and  print (data)
     #await sio.emit('update_value', data, broadcast=True, include_self=False)

@sio.event
async def values_save(sid, data):
     sio_debug and  print (data)

@sio.on('value_changed')
async def value_changed(sid, message):
    sio_debug and print (message)
    global values
    values[message['who']] = message['data']
    await sio_event_post('sample-event', data='emit-data', room='some_room')
    await sio.emit('update_value', message, broadcast=True, include_self=False)



if __name__ == "__main__":
    # https://www.fatalerrors.org/a/uvicorn-a-lightweight-and-fast-python-asgi-framework.html
    #uvicorn.run(app=app, host="127.0.0.1", port=5000, log_level="info")
    uvicorn.run(app=SERV_APP_FILE , host="127.0.0.1", port=PORT, reload=True, workers=1, debug=False)
