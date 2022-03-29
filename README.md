## lvsio - py4web apps

---------------------------------------------
ssep4w - experiment with sse (py4web with rocket3)

used code from :

https://github.com/jakubroztocil/chat/blob/master/app.py

https://gist.github.com/platdrag/e755f3947552804c42633a99ffd325d4

https://maxhalford.github.io/blog/flask-sse-no-deps/

https://stackoverflow.com/questions/31948285/display-data-streamed-from-a-flask-view-as-it-updates/31951077#31951077


tips: run the backgrounder sse task with 

./sse-listen in the same terminal and 

./sse-emit-ping in another terminal



---------------------------------------------


Inspired by flask-meld

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
