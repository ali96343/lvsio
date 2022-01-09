import logging
from ombott.server_adapters import ServerAdapter

import socketio  # pip install python-socketio
import time   #, urllib

import httpx, os, sys


wsservers_list = [
    "tornadoSioWsServer",
]

# --------------------------------------- tornado + websocket + socketio + sockjs ------------------


# copy-past from mlvsio/chan_conf.py

p4w_host = '127.0.0.1'
p4w_port = '8000'
P4W_APP = 'flvsio'
#P4W_APP = 'tlvsio'

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


# Echo the client's ID back to them when they connect.
# io.on('connection', function(client) {
#    client.emit('register', client.id);
# });

    @sio.event
    async def connection(sid, environ):
        sio_debug and print("sio: connect ", sid)
        print ('+++ ',sid)


    @sio.event
    async def connect(sid, environ):
        sio_debug and print("sio: connect ", sid)
        await sio.emit("longtask_register", sid)

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

