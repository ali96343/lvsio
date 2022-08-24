## lvsio - py4web apps
---------------------------------------------

fgrid - grid.js and tabulator.js in py4web app

based on https://blog.miguelgrinberg.com/post/beautiful-flask-tables-part-2

---------------------------------------------

lmenu - layout.html with navigation left_menu 


---------------------------------------------

ssep4w/server_adapters.py 

the file server_adapters.py contains a wsgiref server version 

with a redirector-http->https and ssl-keys

to use, copy the file server_adapters.py  to py4web/server_adapters.py

---------------------------------------------
ssep4w - generators in py4web-controllers 

( polling, server sent events, file-push, live charts ... etc )

run  ./py4web.py run apps --watch=off -s wsgirefThreadingServer  


The following sources were used:

https://github.com/djdmorrison/flask-progress-example

https://ron.sh/creating-real-time-charts-with-flask/

https://github.com/jakubroztocil/chat/blob/master/app.py

https://gist.github.com/platdrag/e755f3947552804c42633a99ffd325d4

https://maxhalford.github.io/blog/flask-sse-no-deps/

https://stackoverflow.com/questions/31948285/display-data-streamed-from-a-flask-view-as-it-updates/31951077#31951077

https://stackoverflow.com/questions/24564030/is-an-eventsource-sse-supposed-to-try-to-reconnect-indefinitely


tips: run the background sse-tasks with the commands

./sse-listen in the same terminal and 

./sse-emit-ping in another terminal

./sse-get-time

---------------------------------------------

py4web with socketio examples

---------------------------------------------

cp mlvsio to apps/

( chan_sio.py - uvicorn channel server )

cd apps/mlvsio && ./chan_sio.py

run py4web

firefox localhost:8000/mlvsio

---------------------------------------------

flvsio is mlvsio with tornado-socketio and sockjs-example

added celery longrun_task from

https://matthewminer.com/2015/02/21/pattern-for-async-task-queue-results

( To test it, you need to run the  file . worker.sh  )

socketio events moved to wsservers.py

copy flvsio/wsservers.py to py4web/utils/wsservers.py

( you can remove twisted and aiohttp  from the wsservers.py, 
  you need install packages from wsservers.py  )

./py4web.py  run -s  tornadoSioWsServer apps

(If the py4web.py cannot find the server tornadoSioWsServer, 
it means you have not installed all the packages from the file wsservers.py)


Note - the name of the application (flvsio) is used in the name of the 
redis-channel in the server file wsservers.py


firefox localhost:8000/flvsio

-------------------------------------------------

lvsio - demo for "how to push event to js-UI from py4web-controllers.py"

cp lvsio to apps/

( chan_sio.py - uvicorn channel server )

cd apps/lvsio && ./chan_3000.py

run py4web

firefox localhost:8000/lvsio

------------------------------------------------

redis must be installed and running

im my /etc/redis.conf: databases 64
