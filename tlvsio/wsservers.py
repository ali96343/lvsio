import logging
from ombott.server_adapters import ServerAdapter

import socketio  # pip install python-socketio
import time   #, urllib

import httpx, os, sys


# tested with py4web version "1.20210905.1"
# This file ( wsservers.py.txt)  contains a websocket-socketio echo servers
# 
# To use it cp wsservers.py.txt wsservers.py, and 
#  you need to install and import additional libraries
#
# pip install python-socketio
# pip install autobahn
# pip install Twisted
# pip install aiohttp
# pip install aiohttp_wsgi

# after installing the libraries for the selected server
#  you can run server from wsservers_list with command

# ./py4web.py  run -s  wsgirefAioSioWsServer  apps
# ./py4web.py  run -s  tornadoSioWsServer  apps
# ./py4web.py  run -s  wsgirefWsTwistedServer  apps


# the echo wsservers can be tested  with py4web/apps/examples

#
# How the servers  from wsservers_list  were tested
# 1 applications were downloaded for testing from https://github.com/ali96343/facep4w
#   ( it's near 8000 files: html+svg+css+png+jpg, 176 py-files, 7000 js-files )
# 2 run py4web with each server
# 3 the time was measured with the script  https://github.com/linkchecker/linkchecker
#   with 10 threads active
# 4 access to the apps databases (sqlite) was not tested.
# 5 that's all
#
# aiohttp  - test duration: 1064 seconds
# tornado  - test duration: 1065 seconds
# twisted  - test duration: 1085 seconds
#
# For the websockets native server handlers are used.
# For the socketio handlers, we use the nice library by Miguel Grinberg - python-socketio.
#
# To test the two installed protocols, please, 
# use two test applications: socketio and ws: firefox localhost:8000/examples
#
# Also at this link https://github.com/ali96343/py4web-chat ,
# there is a more realistic chat server and the file wsservers.py
# also, it is possible copy only one server from this file
# don't forget correct wsservers_list and pip install ....


# https://43.130.48.5/pavlenko-volodymyr/django-sockjs-tornado
# https://mrjoes.github.io/2011/12/14/sockjs-tornado.html
# https://programtalk.com/vs2/?source=python/8806/sockjs-tornado/examples/multiplex/server.py
# https://inmaculados.uv.es/twcam/gestion/src/66c724dc91ea7166d4963b5fabbc8025b3ab43f5/node_modules/sockjs-client


wsservers_list = [
    "tornadoSioWsServer",
    "wsgirefAioSioWsServer",
    "wsgirefWsTwistedServer",
]

# --------------------------- Twisted + websocket -----------------------------------------------


# pip install autobahn
# pip install Twisted


from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol
from autobahn.twisted.resource import WebSocketResource, WSGIRootResource

from twisted.web.resource import Resource


class Hello(Resource):
    isLeaf = True

    def getChild(self, name, request):
        if name == "":
            return self
        return Resource.getChild(self, name, request)

    def render_GET(self, request):
        request.setHeader("Content-Type", "text/html; charset=utf-8")
        return "<html>its my-favicon-robots</html>".encode("utf-8")


ws_debug = False

class WsEcho(WebSocketServerProtocol):
    def onMessage(self, payload, isBinary):
        self.sendMessage(payload, isBinary)

    def onClose(self, wasClean, code, reason):
        ws_debug and print("WebSocket connection closed: ")

    def onConnect(self, request):
        ws_debug and print("Client connecting: {0}".format(request.peer))

    def onOpen(self):
        ws_debug and print("WebSocket connection open.")

    def connectionLost(self, reason):
        """
        Client lost connection, either disconnected or some error.
        Remove client from list of tracked connections.
        """
        pass


def wsgirefWsTwistedServer():

    from twisted.python import log
    import sys

    class TwistedServer(ServerAdapter):
        """
            tested with py4web apps from https://github.com/ali96343/facep4w
            and 10 threads https://github.com/linkchecker/linkchecker
            pydal tested with p4wform (scan url, find forms and insert value)
        """

        def run(self, handler):
            from twisted.web import server, wsgi
            from twisted.python.threadpool import ThreadPool
            from twisted.internet import reactor

            # log.startLogging(sys.stdout)

            wsFactory = WebSocketServerFactory(f"ws://{self.host}:{self.port}/")
            wsFactory.protocol = WsEcho
            wsResource = WebSocketResource(wsFactory)

            myfavi = Hello()

            thread_pool = ThreadPool()
            thread_pool.start()
            reactor.addSystemEventTrigger("after", "shutdown", thread_pool.stop)

            wsgiResource = wsgi.WSGIResource(reactor, thread_pool, handler)
            rootResource = WSGIRootResource(
                wsgiResource,
                {b"": wsResource, b"favicon.ico": myfavi, b"robots.txt": myfavi},
            )

            factory = server.Site(rootResource)

            reactor.listenTCP(self.port, factory, interface=self.host)
            reactor.run()

    return TwistedServer

# END Twisted


# ---------------------- aiohttp + websocket + socketio -----------------------------------------------------

# pip install aiohttp
# pip install aiohttp_wsgi

# https://github.com/aio-libs/sockjs/blob/master/examples/chat.py


def wsgirefAioSioWsServer():
    import logging.handlers
    from aiohttp import web
    from aiohttp_wsgi import WSGIHandler  # pip install aiohttp_wsgi


    # https://pypi.org/project/aiohttp/
    async def handle(request):
        name = request.match_info.get("name", "Anonymous")
        text = "Hello, " + name
        return web.Response(text=text)

    async def wshandle(request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        async for msg in ws:
            if msg.type == web.WSMsgType.text:
                await ws.send_str(f"Echo from ws.aiohttp: {msg.data}")
            elif msg.type == web.WSMsgType.binary:
                await ws.send_bytes(msg.data)
            elif msg.type == web.WSMsgType.close:
                break

        return ws
    
    async def chat_msg_handler(msg, session):
        if session.manager is None:
            return
        if msg.type == sockjs.MSG_OPEN:
            session.manager.broadcast("Someone joined.")
        elif msg.type == sockjs.MSG_MESSAGE:
            session.manager.broadcast(msg.data)
        elif msg.type == sockjs.MSG_CLOSED:
            session.manager.broadcast("Someone left.")
    


    sio_debug = False
    sio = socketio.AsyncServer(async_mode="aiohttp")

    @sio.event
    async def connect(sid, environ):
        sio_debug and print("connect ", sid)

    @sio.event
    async def disconnect(sid):
        sio_debug and print("disconnect ", sid)

    @sio.on("to_py4web")
    async def echo(sid, data):
        sio_debug and print("from client: ", data)
        await sio.emit("py4web_echo", data)

    class AioSioWsServer(ServerAdapter):
        def run(self, app):
            if not self.quiet:
                log = logging.getLogger("loggingAioHttp")
                log.setLevel(logging.INFO)
                log.addHandler(logging.StreamHandler())
            wsgi_handler = WSGIHandler(app)
            app = web.Application()
            sio.attach(app)
            app.router.add_routes([web.get("/", wshandle)])
            app.router.add_route("*", "/{path_info:.*}", wsgi_handler)
            web.run_app(app, host=self.host, port=self.port)

    return AioSioWsServer



# END aiohttp 

# --------------------------------------- tornado + websocket + socketio + sockjs ------------------


# copy-past from mlvsio/chan_conf.py

p4w_host = '127.0.0.1'
p4w_port = '8000'
P4W_APP = 'tlvsio'

sio_PORT = 8000
sio_HOST = p4w_host


r_url = "redis://"

sio_serv_url =  f"http://{sio_HOST}:{sio_PORT}"

sio_room = f'{P4W_APP}_room'
sio_channel = f"sio_{P4W_APP}"
sio_namespaces= ['/','/test','/chat']

post_url = f"http://{p4w_host}:{p4w_port}/{P4W_APP}/sio_chan_post"

BROADCAST_SECRET = "71a30ce5d354bf38a303643212af3bf1d826821539331b091ce7e4218d83d35c"
POST_SECRET = BROADCAST_SECRET



r_url = "redis://"




#  pip install tornado
#  pip install sockjs-tornado
# https://github.com/amagee/sockjs-client/blob/master/sockjs_client.py

def tornadoSioWsServer():

    # py4web.py run -s tornadoSioWsServer apps

    import tornado.websocket
    from tornado.httputil import url_concat
    import tornado.httpclient
    import sockjs.tornado

    ws_debug = True

# https://github.com/mrjoes/sockjs-tornado/tree/master/examples
    
    class SockjsConnection(sockjs.tornado.SockJSConnection):
        """Sockjs connection implementation"""
        # Class level variable
        participants = set()
    
        def on_open(self, info):
            # Send that someone joined
            self.broadcast(self.participants, "Someone joined.")
    
            # Add client to the clients list
            self.participants.add(self)
    
        def on_message(self, message):
            # Broadcast message
            self.broadcast(self.participants, message)
    
        def on_close(self):
            # Remove client from the clients list and broadcast leave message
            self.participants.remove(self)
    
            self.broadcast(self.participants, "Someone left.")
    
    
    class web_socket_handler(tornado.websocket.WebSocketHandler):
        # This class handles the websocket channel
        #@classmethod
        #def route_urls(cls):
        #    return (r"/", cls, {})

        def simple_init(self):
            self.last = time.time()
            self.stop = False

        def open(self):
            #    client opens a connection
            self.simple_init()
            ws_debug and print(
                f"tornado ws: {time.time() - self.last:.1f}: New client connected"
            )
            self.write_message(
                f"tornado ws: {time.time() - self.last:.1f}: You are connected"
            )

        def on_message(self, message):
            #    Message received on the handler
            ws_debug and print(
                f"Echo from tornado ws: {time.time() - self.last:.1f}: received message {message}"
            )
            self.write_message(
                f"ECho from tornado ws: {time.time() - self.last:.1f}: You said - {message}"
            )
            self.last = time.time()

        def on_close(self):
            #    Channel is closed
            ws_debug and print(
                f"tornado ws: {time.time() - self.last:.1f}: connection is closed"
            )
            self.stop = True

        def check_origin(self, origin):
            return True

    def handle_request(response):
        pass

    import socketio

    sio_debug = False
    #sio = socketio.AsyncServer(async_mode="tornado")

# ----------------------------------------------------------------
    r_mgr = socketio.AsyncRedisManager(r_url, channel=sio_channel,  write_only=False)
    sio = socketio.AsyncServer(
        async_mode="tornado",
        client_manager=r_mgr,
        cors_allowed_origins="*",
        #SameSite=None,
        #logger=True,
        #engineio_logger=True,
    )
    #sio = socketio.ASGIApp(sio, static_files={"/": "./chan_public/index.html"})
    
# ----------------------------------------------------------------




    @sio.event
    async def connect(sid, environ):
        sio_debug and print("sio: connect ", sid)

    @sio.event
    async def disconnect(sid):
        sio_debug and print("sio: disconnect ", sid)

    @sio.on("to_py4web")
    async def echo(sid, data):
        sio_debug and print("sio: from client: ", data)
        await sio.emit("py4web_echo", data)

        # http_client = tornado.httpclient.AsyncHTTPClient()
        # params = {"a": 1, "b": 2}
        # request = url_concat("http://localhost:8000/_socketio/echo", params)
        # request = url_concat("http://localhost:8000/_socketio/echo/xx/yy/zz")

        # http_client.fetch(request, handle_request)

# ---------------------------------------------------------------------------

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
    
    



# ---------------------------------------------------------------------------


    class TornadoSioWsServer(ServerAdapter):
        def run(self, handler):  # pragma: no cover
            if not self.quiet:
                log = logging.getLogger("tornadoSioWs")
                log.setLevel(logging.DEBUG)
                log.addHandler(logging.StreamHandler())

            import tornado.wsgi, tornado.httpserver, tornado.web, tornado.ioloop

            container = tornado.wsgi.WSGIContainer(handler)
            SockjsRouter = sockjs.tornado.SockJSRouter(SockjsConnection, '/sockjs')
            app = tornado.web.Application(
                SockjsRouter.urls +  [
                    (r"/", web_socket_handler),
                    (r"/socket.io/", socketio.get_tornado_handler(sio)),
                    (r".*", tornado.web.FallbackHandler, dict(fallback=container)),
                ] 
            )
            server = tornado.httpserver.HTTPServer(app)
            server.listen(port=self.port, address=self.host)

            tornado.ioloop.IOLoop.instance().start()

    return TornadoSioWsServer

# END TORNADO

#-------------------------------------------------------------------

# --------------------------- sio - utils ----------------------------------------------


    
async def sio_event_post(event_name, data=None, room=None, post=True):

    # https://zetcode.com/python/httpx/

    json_data = {
        "event_name": event_name,
        "data": data,
        "room": sio_room, #room,
        "broadcast_secret": BROADCAST_SECRET,
    }

    headers = {'X-Custom': 'value'}

    headers = {
            'app-param': P4W_APP,
            'content-type': "application/json",
            'cache-control': "no-cache"
    }


    async with httpx.AsyncClient() as client:
        r = await client.post(post_url, json=json_data, headers=headers)

        if r.status_code != 200:
            print(f"error! can not post to: {post_url}")




