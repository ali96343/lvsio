## lvsio - py4web apps

Inspired by flask-meld

py4web with socketio examples

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

( you can remove twisted and aiohttp  from the wsservers.py, 
  you need install packages from wsservers.py  )

./py4web.py  run -s  tornadoSioWsServer apps

(If the py4web.py cannot find the server tornadoSioWsServer, 
it means you have not installed all the packages from the file wsservers.py)

( do not run the file chan_sio.py )

( the script does not use an additional port for socketio )


firefox localhost:8000/tlvsio

-------------------------------------------------

lvsio - demo for "how to push event to js-UI from py4web-controllers.py"

cp lvsio to apps/

( chan_sio.py - uvicorn channel server )

cd apps/lvsio && ./chan_3000.py

run py4web

firefox localhost:8000/lvsio

------------------------------------------------

redis must be installed and running
