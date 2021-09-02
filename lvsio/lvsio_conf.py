import sys, os



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
P4W_APP =  __file__.replace('/./','/').split('/')[-1]

sio_debug and print(f"===: {SERV_APP_FILE}")
post_url = f"http://127.0.0.1:8000/{P4W_APP}/from_uvicorn"
BROADCAST_SECRET = "123secret"

