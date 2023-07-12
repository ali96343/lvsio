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
    "tornadoMig",
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

    return  level if level in ( logging.CRITICAL, logging.ERROR, logging.WARN, logging.INFO,
            logging.DEBUG, logging.NOTSET,) else logging.WARN

def logging_conf(level, log_file="server-py4web.log"):
    logging.basicConfig(
        filename=log_file,
        format="%(threadName)s | %(message)s",
        filemode="w",
        encoding="utf-8",
        level=check_level(level),
    )


def get_workers(opts, default=10):
    return opts["workers"] if "workers" in opts else default


# ---------------------------------------------------------------------


def gevent():
    # gevent version 22.10.2

    from gevent import pywsgi, local  # pip install gevent
    import threading

    if not isinstance(threading.local(), local.local):
        msg = "Ombott requires gevent.monkey.patch_all() (before import)"
        raise RuntimeError(msg)

    # ./py4web.py run apps --watch=off -s gevent -L 20  # look into server-py4web.log 
    #
    # ./py4web.py run apps -s gevent --watch=off --port=8443 --ssl_cert=cert.pem --ssl_key=key.pem -L 0
    # ./py4web.py run apps -s gevent --watch=off --host=192.168.1.161 --port=8443 --ssl_cert=server.pem -L 0

    class GeventServer(ServerAdapter):
        def run(self, handler):
            logger = "default"  # not None - from gevent doc

            if not self.quiet:
                logger = logging.getLogger("gevent")
                fh = logging.FileHandler("server-py4web.log")
                logger.setLevel(check_level(self.options["logging_level"]))
                logger.addHandler(fh)
                logger.addHandler(logging.StreamHandler())

            certfile = self.options.get("certfile", None)

            ssl_args = dict(
                    certfile=certfile,
                    keyfile=self.options.get("keyfile", None),
                    ssl_version=ssl.PROTOCOL_SSLv23,
                    server_side=True,
                    do_handshake_on_connect=False,
                ) if certfile else dict()

            server = pywsgi.WSGIServer(
                (self.host, self.port),
                handler,
                log=logger,
                error_log=logger,
                **ssl_args,
            )

            server.serve_forever()

    return GeventServer


def geventWebSocketServer():
    from gevent import pywsgi

    # from geventwebsocket.handler import WebSocketHandler # pip install gevent-websocket
    from gevent_ws import WebSocketHandler  # pip install gevent gevent-ws

    # https://stackoverflow.com/questions/5312311/secure-websockets-with-self-signed-certificate

    # https://pypi.org/project/gevent-ws/
    # ./py4web.py run apps -s geventWebSocketServer --watch=off --ssl_cert=server.pem -H 192.168.1.161 -P 9000 -L 10

    # vi apps/_websocket/templates/index.html    set: ws, wss, host, port
    # firefox http://localhost:8000/_websocket
    # firefox https://192.168.1.161:9000/_websocket  test wss

    # wss-ssl-test.sh
    # HOST=192.168.1.161:9000
    # curl --insecure --include --no-buffer \
    #   -I -H 'Upgrade: websocket' \
    #   -H "Sec-WebSocket-Key: `openssl rand -base64 16`" \
    #   -H 'Sec-WebSocket-Version: 13' \
    #   -sSv  https://$HOST/
    # openssl s_client -showcerts -connect $HOST

    class GeventWebSocketServer(ServerAdapter):
        def run(self, handler):
            logger = "default"  # not None !! from gevent doc

            if not self.quiet:
                logging_conf( self.options["logging_level"],)
                logger = logging.getLogger("gevent-ws")
                logger.addHandler(logging.StreamHandler())

            certfile = self.options.get("certfile", None)

            ssl_args = dict(
                    certfile=certfile,
                    keyfile=self.options.get("keyfile", None),
                ) if certfile else dict()

            server = pywsgi.WSGIServer(
                (self.host, self.port),
                handler,
                handler_class=WebSocketHandler,
                log=logger,
                error_log=logger,
                **ssl_args,
            )

            server.serve_forever()

    return GeventWebSocketServer


def wsgirefThreadingServer():
    # https://www.electricmonk.nl/log/2016/02/15/multithreaded-dev-web-server-for-the-python-bottle-web-framework/

    import socket
    from concurrent.futures import ThreadPoolExecutor  # pip install futures
    from socketserver import ThreadingMixIn
    from wsgiref.simple_server import WSGIRequestHandler, WSGIServer, make_server

    # redirector http -> https ----------------------

    class Redirect:
        # https://www.elifulkerson.com/projects/http-https-redirect.php
        __slots__ = ("sock", "ip", "host", "port", "logger", "client_closed", "fileno")

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
        __slots__ = ( "sock", "certfile", "keyfile", "allow_http", "host", "port", "logger", "fileno",)

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
                logging_conf(
                    self.options["logging_level"],
                )
                self.log = logging.getLogger("WSGIRef")
                self.log.addHandler(logging.StreamHandler())

            self_run = self  # used in internal classes to access options and logger

            class PoolMixIn(ThreadingMixIn):
                def process_request(self, request, client_address):
                    self.pool.submit(
                        self.process_request_thread, request, client_address
                    )

            class ThreadingWSGIServer(PoolMixIn, WSGIServer):
                daemon_threads = True
                pool = ThreadPoolExecutor(
                    max_workers=get_workers(self.options, default=40)
                )

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
                        os.system( f"[[  $(command -v fuser) ]] && fuser -v  {self.port}/tcp")
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
                logging_conf( self.options["logging_level"],)
                log = logging.getLogger("Rocket")
                log.addHandler(logging.StreamHandler())

            interface =  ( self.host, self.port, self.options["keyfile"], self.options["certfile"],
                ) if ( self.options.get("certfile", None) and self.options.get("keyfile", None)
                ) else (self.host, self.port)

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
                logging_conf( self.options["logging_level"],)
                log = logging.getLogger("Pyruvate")
                log.addHandler(logging.StreamHandler())

            pyruvate.serve( handler, f"{self.host}:{self.port}", get_workers(self.options, default=10),)

    return srvPyruvate


# --------------------------------------- tornado + socketio ------------------

# version 0.0.1

def tornadoMig():
    # ./py4web.py  run apps -s tornadoMig --ssl_cert=cert.pem --ssl_key=key.pem
    # ./py4web.py  run apps -s tornadoMig --ssl_cert=cert.pem --ssl_key=key.pem -H 192.168.1.161 -P 9000
    #  curl -k "https://127.0.0.1:8000/socket.io/?EIO=4&transport=polling"

    import tornado, socketio, httpx, uuid, asyncio, uvloop
    import random

    # pip install httpx celery python-socketio

    # sse https://gist.github.com/mivade/d474e0540036d873047f
    # https://alessandro-negri-34754.medium.com/python-add-ssl-to-a-tornado-app-redirect-from-http-to-https-c5625e6bc039
    # https://stackoverflow.com/questions/18353035/redirect-http-requests-to-https-in-tornado

    # https://github.com/tornadoweb/tornado/blob/master/demos/chat/chatdemo.py

    class TornadoMig(ServerAdapter):
        import tornado.wsgi, tornado.httpserver, tornado.ioloop

        # mypep: Z == self ;)

        def run(Z, handler):  

            Z.queue = asyncio.Queue() # https://stackoverflow.com/questions/55693699/how-to-mix-async-socket-io-with-aiohttp
            # response = await queue.get()  # block until there is something in the queue
            # await queue.put(data)

            # https://testdriven.io/blog/developing-an-asynchronous-task-queue-in-python/

            Z.sids_connected = dict()
            # Z.sids_connected[sid] = { "sid": sid, "app_nm": app_nm, "func": func_nm, "username": username, "room": myroom}

            Z.client_count = 0
            Z.a_count = 0
            Z.b_count = 0

            # must exist in apps-controllers
            Z.post_prefix = "/siopost123"

            def get_post_uri(handl):
                post_prefix = f"https://{Z.host}:{Z.port}/" if Z.options.get("certfile", None) else (f"http://{Z.host}:{Z.port}/")
                maybe =  { x.split("/")[0]: x.split("/")[1] for x in handl.routes.keys() if Z.post_prefix in x } 
                post_to = { k: post_prefix + k + '/' + v  for k,v in maybe.items() }
                if not post_to:
                     sys.exit (f'can not find app with controller {Z.post_prefix}')
                return post_to

            Z.post_to = get_post_uri(handler)

            Z.log = None

            if not Z.quiet:
                logging_conf( Z.options["logging_level"],)
                Z.log = logging.getLogger("tornadoMig")
                Z.log.addHandler(logging.StreamHandler())

            def log_info(data):
                Z.log and Z.log.info(data)

            # ------------------------------------------------------------------------------------
            async def post_event( sid, event_name, data=None,):
                app_nm= None
                if sid in Z.sids_connected:
                    sid_data = Z.sids_connected[sid]
                    app_nm = sid_data["app_nm"]
                    if not app_nm in Z.post_to:
                        log_info(f"post_event bad app_nm={app_nm}")
                        return f"app_nm {app_nm} not found in post_to!"
                else:
                    log_info(f"post_event bad sid={sid}")
                    return f"sid {sid} not found in sids_connected!"


                json_data = {
                        "event_name": event_name,
                        "username": sid_data["username"],
                        "data": data,
                        "room": sid_data["room"],  
                        "to": app_nm,
                        "cmd": "cmd",
                        "cmd_args": "cmd_args",
                }

                headers = {
                        "username": sid_data["username"],
                        "app-param": app_nm, 
                        "content-type": "application/json",
                        "cache-control": "no-cache",
                }

                post_url =  Z.post_to[app_nm] 
                log_info(post_url)

                async with httpx.AsyncClient(verify=False) as ctrl_p4w:
                    r = await ctrl_p4w.post( post_url, json=json_data, headers=headers,)

                    r.status_code != 200 and log_info( f"httpx.AsyncClient: {post_url} {r.status_code}")

            # ----------------------------------------------------------------
            r_mgr = socketio.AsyncRedisManager( "redis://", channel="channel_tornadoMig", write_only=False)

            sio = socketio.AsyncServer(
                async_mode="tornado",
                client_manager=r_mgr,
                cors_allowed_origins="*",
                # SameSite=None,
                # logger=True,
                # engineio_logger=True,
            )

            # https://github.com/miguelgrinberg/python-socketio/blob/main/examples/server/tornado/app.py
            # https://gist.github.com/mivade/421c427db75c8c5fa1d1
            # https://github.com/miguelgrinberg/quick-socketio-tutorial/tree/part7

            # ----------------------------------------------------------------

            # https://blog.miguelgrinberg.com/post/learn-socket-io-with-python-and-javascript-in-90-minutes
            # https://github.com/miguelgrinberg/python-socketio/blob/main/examples/server/aiohttp/app.py
            # https://www.twilio.com/blog/asynchronous-http-requests-in-python-with-aiohttp

            async def periodic_task(sid):
                """Example of how to send server generated events to clients."""
                e_name = sys._getframe().f_code.co_name
                count = 0
                while True:
                    count += 1
                    
                    if not sid in Z.sids_connected: break

                    await sio.emit( "my_response", {"data": f"periodic_task 7-sec-counter {count} to {sid}  "},)
                    await post_event( sid, e_name, data={"cmd": "cmd", "cmd_args": "cmd_args", "sid": sid, "count": count } )
                    await sio.sleep(7)

            async def simple_task(sid):
                e_name = sys._getframe().f_code.co_name
                await sio.sleep(5)
                result = await sio.call("mult", {"numbers": [3, 4]}, to=sid)
                log_info(f"result from js-mult: {result}")
                await post_event(sid, e_name, )

            @sio.event
            async def close_room(sid, message):
                e_name = sys._getframe().f_code.co_name
                await sio.emit(
                    "my_response",
                    {"data": "Room " + message["room"] + " is closing."},
                    room=message["room"],
                )
                await sio.close_room(message["room"])

            @sio.event
            async def connect( sid, environ,):
                e_name = sys._getframe().f_code.co_name

                url, func_nm, app_nm = None, None, None

                try:
                    url = environ["HTTP_REFERER"]
                except KeyError:
                    url = environ["HTTP_ORIGIN"]
                    log_info(f"bad url {url}")
                    return False

                url_items = url.rsplit("/")  
                app_nm = url_items[3] if len(url_items) >= 4 else None
                if not app_nm in Z.post_to: #Z.p4w_apps_names:
                    log_info(f"bad app_nm: {app_nm}")
                    return False

                func_nm = url_items[4] if len(url_items) >= 5 else None

                username = environ.get("HTTP_X_USERNAME")
                log_info(f"HTTP_X_USERNAME: {username} {app_nm}")
                if not username:
                    return False

                async with sio.session(sid) as session:
                    session["username"] = username
                    session["sid"] = sid
                    #session["qu"] = asyncio.Queue() 
                await sio.emit("user_joined", f"{username} sid: {sid}")

                # end auth etc

                Z.client_count += 1
                log_info(f"{sid} connected")


                myroom= None
                if random.random() > 0.5:
                    sio.enter_room(sid, "a")
                    myroom="a" 
                    Z.a_count += 1
                    await sio.emit("room_count", Z.a_count, to="a")
                else:
                    sio.enter_room(sid, "b")
                    myroom="b" 
                    Z.b_count += 1
                    await sio.emit("room_count", Z.b_count, to="b")

                Z.sids_connected[sid] = { "sid": sid, "app_nm": app_nm, "func": func_nm, "username": username, "room": myroom}

                await sio.emit("client_count", f"{Z.client_count} {set(Z.sids_connected.keys())}")
                #await sio.emit("client_count", Z.client_count)

                sio.start_background_task(simple_task, sid)
                sio.start_background_task(periodic_task, sid)

                await post_event(sid, e_name, )

                #  curl -k "https://192.168.1.161:9000/socket.io/?EIO=4&transport=polling" -v

            @sio.event
            async def disconnect_request(sid):
                e_name = sys._getframe().f_code.co_name
                await sio.disconnect(sid)

            @sio.event
            async def disconnect(sid):
                e_name = sys._getframe().f_code.co_name

                if sid in Z.sids_connected: del Z.sids_connected[sid]

                Z.client_count -= 1
                log_info(f"{sid} disconnected")
                await sio.emit("client_count", Z.client_count)
                if "a" in sio.rooms(sid):
                    Z.a_count -= 1
                    await sio.emit("room_count", Z.a_count, to="a")
                else:
                    Z.b_count -= 1
                    await sio.emit("room_count", Z.b_count, to="b")

                async with sio.session(sid) as session:
                    await sio.emit("user_left", session["username"])


            @sio.event
            async def sum(sid, data):
                e_name = sys._getframe().f_code.co_name
                # log_info(data)
                result = data["numbers"][0] + data["numbers"][1]
                return {"result": result}

            # ------------------------- ImaSize ------------------------------

            @sio.event
            async def js_image_resize(sid, data):
                e_name = sys._getframe().f_code.co_name
                log_info(f"sio {e_name}: {data}")
                data = {"xxxx": "yyyy"}
                await post_event(sid, e_name, data=data,)

            # ---------------------------Counter------------------------------

            @sio.event
            async def js_count(sid, data):
                e_name = sys._getframe().f_code.co_name
                log_info(f"sio {e_name}: {data}")
                data = {"xxxx": "yyyy"}
                await post_event(sid, e_name, data=data, )

            # ---------------------- Sliders----------------------------------

            @sio.event
            async def js_sliders(sid, data):
                e_name = sys._getframe().f_code.co_name
                log_info(f"sio {e_name}: {data}")
                data = {"xxxx": "yyyy"}
                await post_event(sid, e_name, data=data, )

            # ----------------------------------------------------------------

            # https://github.com/siysun/Tornado-wss/blob/master/main.py
            # https://forum.nginx.org/read.php?2,286850,286879
            # https://telecom.altanai.com/2016/05/17/setting-up-ubuntu-ec2-t2-micro-for-webrtc-and-socketio/
            # curl -k "https://127.0.0.1:8000/socket.io/?EIO=4&transport=polling"

            # https://github.com/tornadoweb/tornado/blob/master/demos/websocket/chatdemo.py
            # https://github.com/tornadoweb/tornado/blob/master/demos/chat/chatdemo.py
            async def main():
                container = tornado.wsgi.WSGIContainer(handler)

                app = tornado.web.Application(
                    [
                        (r"/socket.io/", socketio.get_tornado_handler(sio)),
                        (r".*", tornado.web.FallbackHandler, dict(fallback=container)),
                    ],
                    # cookie_secret=str(uuid.uuid4()),
                    # cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
                    #    xsrf_cookies=True,
                )

                server, certfile, keyfile = None, Z.options.get("certfile", None), Z.options.get("keyfile", None)

                if certfile and keyfile:
                    ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                    ssl_ctx.load_cert_chain(certfile, keyfile)
                    server = tornado.httpserver.HTTPServer(app, ssl_options=ssl_ctx)
                else:
                    server = tornado.httpserver.HTTPServer(app)

                server.listen(port=Z.port, address=Z.host)
                await asyncio.Event().wait()

            # tornado.ioloop.IOLoop.instance().start() #
            # asyncio.run(main())

            if sys.version_info >= (3, 11):
                with asyncio.Runner(loop_factory=uvloop.new_event_loop) as runner:
                    runner.run(main())
            else:
                uvloop.install()
                asyncio.run(main())

    return TornadoMig


# curl -X GET "http://localhost:8000/socket.io/?EIO=4&transport=polling"
# https://github.com/socketio/socket.io-protocol#packet-encoding

# https://stackoverflow.com/questions/41026351/create-process-in-tornado-web-server

# https://rob-blackbourn.medium.com/secure-communication-with-python-ssl-certificate-and-asyncio-939ae53ccd35


# https://stackoverflow.com/questions/34759841/using-tornado-with-aiohttp-or-other-asyncio-based-libraries


# https://habr.com/ru/companies/wunderfund/articles/702484/
# Полное руководство по модулю asyncio в Python. Часть 3
# https://stackoverflow.com/questions/72725651/how-to-remove-value-from-list-safely-in-asyncio
# https://codereview.stackexchange.com/questions/228868/structure-and-code-of-tornado-webapp
# https://stackoverflow.com/questions/17148732/how-to-iterate-through-dictionary-passed-from-python-tornado-handler-to-tornado
# https://www.georgeho.org/tornado-websockets/
# https://stackoverflow.com/questions/52596096/flask-socketio-redis-subscribe

# mk_cert_pem_key_pem.sh
"""
!/ban/bash
openssl \
 req -x509 \
 -newkey rsa:4096 \
 -nodes \
 -out cert.pem \
 -keyout key.pem \
 -days 365 \
 -subj "/C=RU/ST=Saint Petersburg/O=SPB/OU=AliBsk/CN=localhost/emailAddress=ab96343@gmail.com"
"""

#mk_server_pem.sh
"""
!/ban/bash
openssl \
 req -x509 \
 -newkey rsa:4096 \
 -keyout server.pem \
 -out server.pem \
 -days 365 \
 -nodes \
 -subj "/C=RU/ST=Saint Petersburg/O=SPB/OU=AliBsk/CN=localhost/emailAddress=ab96343@gmail.com"
"""
