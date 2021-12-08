## lvsio - py4web app

chan_sio.py - uvicorn channel server

cp mlvsio to apps/

cd apps/mlvsio && ./chan_sio.py

run py4web

firefox localhost:8000/mlvsio

---------------------------------------------

tlvsio is mlvsio with tornado-socketio and sockjs

socketio events moved to wsservers.py

copy tlvsio/wsservers.py to py4web/utils/wsservers.py

./py4web.py  run -s  tornadoSioWsServer  apps --watch="off"

( do not run the file chan_sio.py )

( the script does not use an additional port for socketio )


firefox localhost:8000/tlvsio

-------------------------------------------------


