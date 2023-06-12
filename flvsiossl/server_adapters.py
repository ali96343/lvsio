import logging, ssl, sys, os

from ombott.server_adapters import ServerAdapter

try:
    from .utils.wsservers import *
except ImportError:
    wsservers_list = []

__all__ = [
    "gevent",
    "geventWebSocketServer",
    "wsgirefThreadingServer",
    "rocketServer",
    "Pyruvate",
    "tornadoSio",
] + wsservers_list

# ---------------------- utils -----------------------------------------------

def check_level(level):

     # lib/python3.7/logging/__init__.py
     # CRITICAL = 50
     # FATAL = CRITICAL
     # ERROR = 40
     # WARNING = 30
     # WARN = WARNING
     # INFO = 20
     # DEBUG = 10
     # NOTSET = 0

     return level if level in ( logging.CRITICAL, logging.ERROR, logging.WARN, 
                  logging.INFO, logging.DEBUG, logging.NOTSET ) else logging.WARN

def logging_conf( level, log_file="server-py4web.log"):

     logging.basicConfig(
         filename=log_file,
         format="%(threadName)s | %(message)s",
         filemode="w",
         encoding="utf-8",
         level=check_level( level ) ,
     )

def get_workers(opts, default = 10):     
    return opts['workers'] if 'workers' in opts else default

# ---------------------------------------------------------------------    

def gevent():
    # gevent version 22.10.2

    from gevent import pywsgi, local # pip install gevent
    import threading

    if not isinstance(threading.local(), local.local):
        msg = "Ombott requires gevent.monkey.patch_all() (before import)"
        raise RuntimeError(msg)


    # ./py4web.py run apps --watch=off -s gevent -L 20  # look into gevent.log
    #
    # ./py4web.py run apps -s gevent --watch=off --port=8443 --ssl_cert=cert.pem --ssl_key=key.pem -L 0
    # ./py4web.py run apps -s gevent --watch=off --host=192.168.1.161 --port=8443 --ssl_cert=server.pem -L 0

    class GeventServer(ServerAdapter):
        def run(self, handler):

            logger ='default' # not None - from gevent doc
            if not self.quiet:
          
                logger = logging.getLogger('gevent')
                fh = logging.FileHandler('server-py4web.log')
                logger.setLevel( check_level( self.options["logging_level"] ) )
                logger.addHandler( fh )
                logger.addHandler(logging.StreamHandler())

            certfile = self.options.get("certfile", None)

            ssl_args = dict (
                     certfile = certfile,
                     keyfile = self.options.get("keyfile", None),
                     ssl_version=ssl.PROTOCOL_SSLv23,
                     server_side= True,
                     do_handshake_on_connect=False,
                ) if certfile else dict()

            server = pywsgi.WSGIServer(
                (self.host, self.port),
                handler,
                log=logger, error_log=logger,
                **ssl_args
            )

            server.serve_forever()

    return GeventServer


def geventWebSocketServer():
    from gevent import pywsgi  # pip install gevent gevent-ws
    #from geventwebsocket.handler import WebSocketHandler # pip install gevent-websocket
    from gevent_ws import WebSocketHandler

    # https://stackoverflow.com/questions/5312311/secure-websockets-with-self-signed-certificate

    # https://pypi.org/project/gevent-ws/
    # ./py4web.py run apps -s geventWebSocketServer --watch=off --ssl_cert=server.pem -H 192.168.1.161 -P 9000 -L 10
  
    # vi apps/_websocket/templates/index.html    set: ws, wss, host, port
    # firefox http://localhost:8000/_websocket
    # firefox https://192.168.1.161:9000/_websocket  test wss

    #wss-ssl-test.sh
    #HOST=192.168.1.161:9000
    # curl --insecure --include --no-buffer \
    #   -I -H 'Upgrade: websocket' \
    #   -H "Sec-WebSocket-Key: `openssl rand -base64 16`" \
    #   -H 'Sec-WebSocket-Version: 13' \
    #   -sSv  https://$HOST/
    #openssl s_client -showcerts -connect $HOST


    class GeventWebSocketServer(ServerAdapter):
        def run(self, handler):

            logger='default' # not None !! from gevent doc
            if not self.quiet:
                logging_conf(self.options["logging_level"], )
                logger = logging.getLogger("gevent-ws")
                logger.addHandler(logging.StreamHandler())

            certfile = self.options.get("certfile", None)

            ssl_args = dict (
                     certfile = certfile,
                     keyfile = self.options.get("keyfile", None),
                ) if certfile else dict()

            server = pywsgi.WSGIServer(
                (self.host, self.port),
                handler,
                handler_class=WebSocketHandler,
                log=logger, error_log=logger,
                **ssl_args
            )

            server.serve_forever()

    return GeventWebSocketServer


def wsgirefThreadingServer():
    # https://www.electricmonk.nl/log/2016/02/15/multithreaded-dev-web-server-for-the-python-bottle-web-framework/

    import socket
    from concurrent.futures import ThreadPoolExecutor  # pip install futures
    from socketserver import ThreadingMixIn
    from wsgiref.simple_server import (WSGIRequestHandler, WSGIServer, make_server)


    # redirector http -> https ----------------------

    class Redirect:
        # https://www.elifulkerson.com/projects/http-https-redirect.php
        __slots__ = ( 'sock', 'ip', 'host', 'port', 'logger','client_closed','fileno')
        def __init__(self, socket, address, host="127.0.0.1", port=8000, logger=None):
            self.sock = socket
            self.ip = address[0]
            self.host = host
            self.port = str(port)
            self.logger = logger
            self.client_closed = False
            for m in ["fileno"]:
                setattr(self, m, getattr(self.sock, m))

        def sendline(self, data):
            if not self.client_closed:
                try:
                    self.sock.send(data + b"\r\n")
                except (ConnectionResetError, BrokenPipeError):
                    self.client_closed = True

        def __call__(self):
            go_to = f"https://{self.host}:{self.port}".encode()
            method = b"UNKNOWN"
            data = self.sock.recv(1024)

            if data:
                req_url = data.split(b" ", 2)
                if req_url and req_url[2].startswith(b"HTTP/1.1\r\n"):
                    go_to += req_url[1]
                    method = req_url[0]

                self.sendline(b"HTTP/1.1 302 Encryption Required")
                self.sendline(b"Location: " + go_to)
                self.sendline(b"Connection: close")
                self.sendline(b"Cache-control: private")
                self.sendline(b"")

                self.sendline(
                    b"<html><body>Encryption Required <a href='"
                    + go_to
                    + b"'>"
                    + b"go_to"
                    + b"</a></body></html>"
                )
                self.sendline(b"")

            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
            if self.logger:
                dt = datetime.datetime.now().strftime("%d/%b/%Y %H:%M:%S")
                self.logger.info(
                    f'{self.ip} - - [{dt}] -> "{go_to.decode()}" {method.decode()}'
                )

    class Is_Https:
        # https://stackoverflow.com/questions/13325642/python-magic-smart-dual-mode-ssl-socket
        __slots__ = ( 'sock', 'certfile', 'keyfile', 'allow_http', 'host', 'port', 'logger', 'fileno')
        def __init__( self, socket, certfile, keyfile, allow_http=False, host="127.0.0.1", port=8000, logger=None,):
            self.sock = socket
            self.certfile = certfile
            self.keyfile = keyfile
            self.allow_http = allow_http
            self.host = host
            self.port = str(port)
            self.logger = logger
            for m in ["fileno"]:
                setattr(self, m, getattr(self.sock, m))
    
        def accept(self):
            (conn, addr) = self.sock.accept()
            if conn.recv(1, socket.MSG_PEEK) == b"\x16":
                return (
                    ssl.wrap_socket(
                        conn,
                        certfile=self.certfile,
                        keyfile=self.keyfile,
                        do_handshake_on_connect=False,
                        server_side=True,
                        ssl_version=ssl.PROTOCOL_SSLv23,
                    ),
                    addr,
                )
            elif self.allow_http:
                return (conn, addr)
            else:
                Redirect(conn, addr, self.host, self.port, self.logger)()
                conn.shutdown(socket.SHUT_RDWR)
                conn.close()
                return (conn, addr)

    # end redirector http -> https ----------------------

    class WSGIRefThreadingServer(ServerAdapter):
        def run(self, app):
            
            self.log = None
            if not self.quiet:
                logging_conf(self.options["logging_level"], )
                self.log = logging.getLogger("WSGIRef")
                self.log.addHandler(logging.StreamHandler())

            self_run = self # used in internal classes to access options and logger

            class PoolMixIn(ThreadingMixIn):
                def process_request(self, request, client_address):
                    self.pool.submit(
                        self.process_request_thread, request, client_address
                    )

            class ThreadingWSGIServer(PoolMixIn, WSGIServer):
                daemon_threads = True
                pool = ThreadPoolExecutor(max_workers=get_workers(self.options, default = 40))

            class Server:
                def __init__( self, server_address=("127.0.0.1", 8000), handler_cls=None):
                    self.wsgi_app = None
                    self.listen, self.port = server_address
                    self.handler_cls = handler_cls

                def set_app(self, app):
                    self.wsgi_app = app

                def get_app(self):
                    return self.wsgi_app

                def serve_forever(self):
                    try:
                        self.server = make_server(
                            self.listen,
                            self.port,
                            self.wsgi_app,
                            ThreadingWSGIServer,
                            self.handler_cls,
                        )
                    except OSError as ex:
                        # install fuser: yum install psmisc, apt-get install psmisc
                        os.system( f"[[  $(command -v fuser) ]] && fuser -v  {self.port}/tcp" )
                        sys.exit(ex)

    
                    # openssl req -newkey rsa:4096 -new -x509 -keyout server.pem -out server.pem -days 365 -nodes
                    # openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
                    # ./py4web.py run apps -s wsgirefThreadingServer --watch=off --port=8443 --ssl_cert=cert.pem --ssl_key=key.pem
                    # openssl s_client -showcerts -connect 127.0.0.1:8443

                    certfile = self_run.options.get("certfile", None)

                    if certfile:
                        self.server.socket = Is_Https(
                            socket=self.server.socket,
                            certfile=certfile,
                            keyfile=self_run.options.get("keyfile", None),
                            host=self.listen,
                            port=self.port,
                            logger=self_run.log,
                        )

                    self.server.serve_forever()

            class LogHandler(WSGIRequestHandler):
                def address_string(self):  # Prevent reverse DNS lookups please.
                    return self.client_address[0]

                def log_request(*args, **kw):
                    if not self_run.quiet:
                        return WSGIRequestHandler.log_request(*args, **kw)

                def log_message(self, format, *args):
                    if not self_run.quiet:  # and ( not args[1] in ['200', '304']) :
                        msg = "%s - - [%s] %s" % (
                            self.client_address[0],
                            self.log_date_time_string(),
                            format % args,
                        )
                        self_run.log.info(msg)

            handler_cls = self.options.get("handler_class", LogHandler)
            server_cls = Server

            if ":" in self.host:  # Fix wsgiref for IPv6 addresses.
                if getattr(server_cls, "address_family") == socket.AF_INET:

                    class server_cls(server_cls):
                        address_family = socket.AF_INET6

            srv = make_server(self.host, self.port, app, server_cls, handler_cls)
            srv.serve_forever()

    return WSGIRefThreadingServer


def rocketServer():
    try:
        from rocket3 import Rocket3 as Rocket
    except ImportError:
        from .rocket3 import Rocket3 as Rocket

    class RocketServer(ServerAdapter):
        def run(self, app):

            if not self.quiet:
             
                logging_conf( self.options["logging_level"], )
                log = logging.getLogger("Rocket")
                log.addHandler(logging.StreamHandler())

            interface = (self.host, self.port, self.options["keyfile"], self.options["certfile"]
                ) if ( self.options.get("certfile", None) and self.options.get("keyfile", None) 
                ) else ( self.host, self.port)

            server = Rocket(interface, "wsgi", dict(wsgi_app=app))
            server.start()

    return RocketServer


def Pyruvate():

    # https://2020.ploneconf.org/talks/pyruvate-a-reasonably-fast-non-blocking-multithreaded-wsgi-server
    # https://maurits.vanrees.org/weblog/archive/2021/10/thomas-schorr-pyruvate-wsgi-server-status-update
    # https://gitlab.com/tschorr/pyruvate
    # https://pypi.org/project/pyruvate/

    # ./py4web.py run apps -s waitressPyruvate -L 20
    #  ./py4web.py run apps -s waitressPyruvate  --watch=off
    
    import pyruvate  # pip install pyruvate

    class srvPyruvate(ServerAdapter):
        def run(self, handler):

            if not self.quiet:

                logging_conf( self.options["logging_level"], )
                log = logging.getLogger("Pyruvate")
                log.addHandler(logging.StreamHandler())

            pyruvate.serve(handler, f"{self.host}:{self.port}", get_workers(self.options, default = 10) )

    return srvPyruvate


# --------------------------------------- tornado + socketio ------------------
# pip install httpx celery


def tornadoSio():

    # ./py4web.py  run apps -s tornadoSio --ssl_cert=cert.pem --ssl_key=key.pem
    # ./py4web.py  run apps -s tornadoSio --ssl_cert=cert.pem --ssl_key=key.pem -H 192.168.1.161 -P 9000
    #  curl -k "https://127.0.0.1:8000/socket.io/?EIO=4&transport=polling"

    from tornado.httputil import url_concat
    import tornado.httpclient
    import socketio  # pip install python-socketio
    import httpx, os, sys

    # sse https://gist.github.com/mivade/d474e0540036d873047f
    # https://alessandro-negri-34754.medium.com/python-add-ssl-to-a-tornado-app-redirect-from-http-to-https-c5625e6bc039
    # https://stackoverflow.com/questions/18353035/redirect-http-requests-to-https-in-tornado

    class TornadoSio(ServerAdapter):
        import tornado.wsgi, tornado.httpserver, tornado.web, tornado.ioloop
        def run(self, handler):  # pragma: no cover

            self.log = None
            if not self.quiet:

                logging_conf( self.options["logging_level"], )
                self.log = logging.getLogger("tornadoSioWs")
                self.log.addHandler(logging.StreamHandler())
                self.log.info('start tornadoSio')

            # ------------------------------------------------------------------------------------   


            P4W_APP = 'flvsiossl'
            
            sio_room = f'{P4W_APP}_room'
            sio_channel = f"sio_{P4W_APP}"
            sio_namespaces= ['/','/test','/chat']
            
            post_url = f"https://{self.host}:{self.port}/{P4W_APP}/sio_chan_post"
            
            BROADCAST_SECRET = "71a30ce5d354bf38a303643212af3bf1d826821539331b091ce7e4218d83d35c"
            POST_SECRET = BROADCAST_SECRET
            
            r_url = "redis://"

            p4w_apps_names = { x.split('/',2)[0] for x in handler.routes.keys() if x } 
            self.log and self.log.info ( p4w_apps_names )
        
            # ----------------------------------------------------------------
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
            
                async with httpx.AsyncClient( verify=False) as client:
                    r = await client.post(post_url, json=json_data, headers=headers, )
            
                    if r.status_code != 200:
                        self.log and self.log.info(f"error! can not post to: {post_url}")
            
            
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
            
            # ----------------------------------------------------------------
        
            @sio.event
            async def connect(sid, environ):
                if self.log:
                    msg = f"sio connect! {sid}:{environ['HTTP_REFERER']}" if ( 
                            'HTTP_REFERER' in environ ) else ( f"sio connect! {sid}:{environ['HTTP_ORIGIN']}" )
                    self.log.info(msg)             
                    #self.log.info(environ)             
                await sio.emit("longtask_register", sid)
        
            @sio.event
            async def disconnect(sid):
                self.log and self.log.info(f"sio: disconnect! {sid} ")
        
            @sio.on("to_py4web")
            async def echo(sid, data):
                self.log and self.log.info("sio: from client: ", data)
                await sio.emit("py4web_echo", data)
        
                # http_client = tornado.httpclient.AsyncHTTPClient()
                # params = {"a": 1, "b": 2}
                # request = url_concat("http://localhost:8000/_socketio/echo", params)
                # request = url_concat("http://localhost:8000/_socketio/echo/xx/yy/zz")
        
                # http_client.fetch(request, handle_request)
        
        
            # ------------------------- ImaSize ------------------------------------------
            
            @sio.event
            async def js_image_resize(sid, data):
                self.log and self.log.info(data)
                e_name = sys._getframe().f_code.co_name
                await sio_event_post( e_name  , data=data, room="some_room")
            
            
            # ---------------------------Counter------------------------------------==
            
            @sio.event
            async def js_count(sid, data):
                self.log and self.log.info(data)
                e_name = sys._getframe().f_code.co_name
                await sio_event_post( e_name  , data=data, room="some_room")
            
            # ---------------------- Sliders--------------------------------------==
            
            @sio.event
            async def js_sliders(sid, data):
                self.log and self.log.info("sio js_sliders: ",data)
                e_name = sys._getframe().f_code.co_name
                await sio_event_post( e_name  , data=data, room="some_room")
        
            # ------------------------------------------------------------------------------------   

            container = tornado.wsgi.WSGIContainer(handler)
            
            app = tornado.web.Application(
                [
                    (r"/socket.io/", socketio.get_tornado_handler(sio)),
                    (r".*", tornado.web.FallbackHandler, dict(fallback=container)),
                ] 
            )


            # https://github.com/siysun/Tornado-wss/blob/master/main.py
            # https://forum.nginx.org/read.php?2,286850,286879
            # https://telecom.altanai.com/2016/05/17/setting-up-ubuntu-ec2-t2-micro-for-webrtc-and-socketio/
            # curl -k "https://127.0.0.1:8000/socket.io/?EIO=4&transport=polling"

            server = tornado.httpserver.HTTPServer(app)

            certfile = self.options.get("certfile", None)
            keyfile = self.options.get("keyfile", None)

            if certfile and keyfile :
                ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                ssl_ctx.load_cert_chain(certfile, keyfile )
                server = tornado.httpserver.HTTPServer(app, ssl_options=ssl_ctx ) 

            server.listen(port=self.port, address=self.host)

            tornado.ioloop.IOLoop.instance().start( )

    return TornadoSio

# END TORNADO

# curl -X GET "http://localhost:8000/socket.io/?EIO=4&transport=polling"
# https://github.com/socketio/socket.io-protocol#packet-encoding

# https://stackoverflow.com/questions/41026351/create-process-in-tornado-web-server

# https://rob-blackbourn.medium.com/secure-communication-with-python-ssl-certificate-and-asyncio-939ae53ccd35


