## lvsio - py4web apps

Inspired by flask-meld

---------------------------------------------

cp mlvsio to apps/

( chan_sio.py - uvicorn channel server )

cd apps/mlvsio && ./chan_sio.py

run py4web

firefox localhost:8000/mlvsio

---------------------------------------------

tlvsio is mlvsio with tornado-socketio and sockjs-example

socketio events moved to wsservers.py

copy tlvsio/wsservers.py to py4web/utils/wsservers.py

( you can remove twisted and aiohttp  from the wsservers.py  )

./py4web.py  run -s  tornadoSioWsServer  apps --watch="off"

( do not run the file chan_sio.py )

( the script does not use an additional port for socketio )


firefox localhost:8000/tlvsio

-------------------------------------------------

redis must be installed and running
