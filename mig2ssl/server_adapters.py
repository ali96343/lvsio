import logging, ssl, sys, os

from ombott.server_adapters import ServerAdapter

# sa_version 0.0.45 ab96343@gmail.com

try:
    from .utils.wsservers import *
except ImportError:
    wsservers_list = []

__all__ = [
    "gevent",
    "geventWebSocketServer",
    "wsgirefThreadingServer",
    "rocketServer",
    # plus 
    "Pyruvate",
    "torMig",
    "aioMig",
] + wsservers_list


# ---------------------- note -----------------------------------------------
# https://www.bitecode.dev/p/asyncio-twisted-tornado-gevent-walk
# https://testdriven.io/guides/flask-deep-dive/
# https://realpython.com/python-click/
# https://github.com/miguelgrinberg/microdot
# https://github.com/Hardtack/Flask-aiohttp/blob/master/flask_aiohttp/helper.py
# https://github.com/Hardtack/Flask-aiohttp
# https://stackoverflow.com/questions/42009202/how-to-call-a-async-function-contained-in-a-class


# ---------------------- utils -----------------------------------------------

# export PY4WEB_LOGS=/tmp # export PY4WEB_LOGS=
def get_log_file():
    log_dir = os.environ.get("PY4WEB_LOGS", None)
    log_file =  os.path.join (log_dir, 'server-py4web.log') if log_dir else None
    if log_file:
        print(f"log_file: {log_file}")
    return log_file    

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

    return (
        level
        if level
        in (
            logging.CRITICAL,
            logging.ERROR,
            logging.WARN,
            logging.INFO,
            logging.DEBUG,
            logging.NOTSET,
        )
        else logging.WARN
    )

# https://stackoverflow.com/questions/35048921/format-log-messages-as-a-tree

def logging_conf(level=logging.WARN, logger_name=__name__):

    log_file = get_log_file()
    log_to = dict()

    if log_file:

        log_to["filename" ] = log_file
        log_to["filemode" ] = "w"

        if sys.version_info >= (3, 9):
            log_to["encoding"] = "utf-8"

    short_msg = "%(message)s > %(threadName)s > %(asctime)s.%(msecs)03d"
    #long_msg = short_msg + " > %(funcName)s > %(filename)s:%(lineno)d > %(levelname)s"

    time_msg = '%H:%M:%S'
    #date_time_msg = '%Y-%m-%d %H:%M:%S'

    try:
        logging.basicConfig(
            format=short_msg,
            datefmt=time_msg,
            level=check_level(level),
            **log_to,
        )
    except ( OSError, ValueError, LookupError, KeyError ) as ex:
        print(f"{ex}, {__file__}")
        print(f'cannot open {log_file}')
        logging.basicConfig( format="%(message)s [%(levelname)s] %(asctime)s", level=check_level(level),)


    if logger_name is None:
        return None

    log = logging.getLogger('SA:' + logger_name)
    log.propagate = True

    #for func in (log.debug, log.info, log.warn, log.error, log.critical, ) :
    #    func('func: ' + func.__name__ )

    return log


def get_workers(opts, default=10):
    try:
        return opts["workers"] if opts["workers"] else default
    except KeyError:
        return default
# ---------------------------------------------------------------------


def gevent():
    # gevent version 23.7.0

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
        def run(self, py4web_apps_handler):
            logger = "default"  

            if not self.quiet:
                logger = logging_conf(
                    self.options["logging_level"], "gevent",
                )

                #logger.addHandler(logging.StreamHandler())

            certfile = self.options.get("certfile", None)

            ssl_args = (
                dict(
                    certfile=certfile,
                    keyfile=self.options.get("keyfile", None),
                    ssl_version=ssl.PROTOCOL_SSLv23,
                    server_side=True,
                    do_handshake_on_connect=False,
                    ca_certs=None,
                    ciphers=None,
                )
                if certfile
                else dict()
            )

            server = pywsgi.WSGIServer(
                (self.host, self.port),
                py4web_apps_handler,
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
        def run(self, py4web_apps_handler):
            logger = "default"  

            if not self.quiet:
                logger = logging_conf(
                    self.options["logging_level"], "gevent-ws", 
                )

            certfile = self.options.get("certfile", None)

            ssl_args = (
                dict(
                    certfile=certfile,
                    keyfile=self.options.get("keyfile", None),
                )
                if certfile
                else dict()
            )

            server = pywsgi.WSGIServer(
                (self.host, self.port),
                py4web_apps_handler,
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
        __slots__ = (
            "sock",
            "certfile",
            "keyfile",
            "allow_http",
            "host",
            "port",
            "logger",
            "fileno",
        )

        def __init__(
            self,
            socket,
            certfile,
            keyfile,
            allow_http=False,
            host="127.0.0.1",
            port=8000,
            logger=None,
        ):
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
                        ca_certs=None,
                        ciphers=None,
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
        def run(self, py4web_apps_handler):

            self.log = None

            if not self.quiet:
                self.log = logging_conf(
                    self.options["logging_level"], "wsgiref", 
                )

            self_run = self  # used in innner classes to access options and logger

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
                def __init__(
                    self, server_address=("127.0.0.1", 8000), handler_cls=None
                ):
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
                        os.system(
                            f"[[  $(command -v fuser) ]] && fuser -v  {self.port}/tcp"
                        )
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
                    #if not self_run.quiet:
                    if self_run.log:
                        return WSGIRequestHandler.log_request(*args, **kw)

                def log_message(self, format, *args):
                    #if not self_run.quiet:  # and ( not args[1] in ['200', '304']) :
                    if self_run.log:  # and ( not args[1] in ['200', '304']) :
                        msg = "%s - - [%s] %s" % (
                            self.client_address[0],
                            self.log_date_time_string(),
                            format % args,
                        )
                        self_run.log.info(msg)

            server_cls = Server

            if ":" in self.host:  # Fix wsgiref for IPv6 addresses.
                if getattr(server_cls, "address_family") == socket.AF_INET:

                    class server_cls(server_cls):
                        address_family = socket.AF_INET6

            srv = make_server(self.host, self.port, py4web_apps_handler, server_cls, LogHandler)
            srv.serve_forever()

    return WSGIRefThreadingServer


def rocketServer():
    try:
        from rocket3 import Rocket3 as Rocket
    except ImportError:
        from .rocket3 import Rocket3 as Rocket

    class RocketServer(ServerAdapter):
        def run(self, py4web_apps_handler):
            if not self.quiet:
                logger = logging_conf(
                    self.options["logging_level"], "Rocket",
                )

            interface = (
                (
                    self.host,
                    self.port,
                    self.options["keyfile"],
                    self.options["certfile"],
                )
                if (
                    self.options.get("certfile", None)
                    and self.options.get("keyfile", None)
                )
                else (self.host, self.port)
            )

            server = Rocket(interface, "wsgi", dict(wsgi_app=py4web_apps_handler))
            server.start()

    return RocketServer


# ----------------------------------------------------------------------------------


def Pyruvate():
    # https://2020.ploneconf.org/talks/pyruvate-a-reasonably-fast-non-blocking-multithreaded-wsgi-server
    # https://maurits.vanrees.org/weblog/archive/2021/10/thomas-schorr-pyruvate-wsgi-server-status-update
    # https://gitlab.com/tschorr/pyruvate
    # https://pypi.org/project/pyruvate/

    # ./py4web.py run apps -s Pyruvate -L 20
    #  ./py4web.py run apps -s Pyruvate  --watch=off

    import pyruvate  # pip install pyruvate

    class srvPyruvate(ServerAdapter):
        def run(self, py4web_apps_handler):
            if not self.quiet:
                log = logging_conf(
                    self.options["logging_level"], "Pyruwate",
                )

            pyruvate.serve(
                py4web_apps_handler,
                f"{self.host}:{self.port}",
                get_workers(self.options, default=10),
            )

    return srvPyruvate


# --------------------------------------- Mig --------------------------------
# alias mig="cd $p4w_path && ./py4web.py run apps -s torMig --ssl_cert=cert.pem --ssl_key=key.pem -H 192.168.1.161 -P 9000 -L 20"

#  curl -k "http://127.0.0.1:8000/socket.io/?EIO=4&transport=polling"
#  curl -k "https://192.168.1.161:9000/socket.io/?EIO=4&transport=polling"

import socketio, httpx, asyncio, json, random

# https://stackoverflow.com/questions/8812715/using-a-simple-python-generator-as-a-co-routine-in-a-tornado-async-handler
# https://gist.github.com/mivade/d474e0540036d873047f

# import socketio, httpx, asyncio, json, random, sys

class MultiSio:
    # Z == self, mypep ;)
    def __init__(Z, handl, host='127.0.0.1', port='8000', certfile=None, keyfile=None, log=None, dbg=True, sio_mode='tornado'):
        Z.handl = handl
        Z.host = host
        Z.port = port
        Z.certfile = certfile
        Z.keyfile = keyfile
        Z.log = log
        Z.dbg = dbg
        Z.sio_mode=sio_mode
        Z.sio = None
        Z.post_to = None
        Z.red_param = None, None
        Z.setup()

    def cprint(Z, mess="mess", color="green", dbg=True, to_file =True):
        c_fmt = "--- {}"
        if sys.stdout.isatty() == True:
            c = {
                "red": "\033[91m {}\033[00m",
                "green": "\033[92m {}\033[00m",
                "yellow": "\033[93m {}\033[00m",
                "cyan": "\033[96m {}\033[00m",
                "gray": "\033[97m {}\033[00m",
                "purple": "\033[95m {}\033[00m",
            }
        c_fmt = c.get(color, c_fmt)
        if to_file == False:
            dbg and print(c_fmt.format(str(mess)))
        else:    
            dbg and Z.log_info(str(mess))

    def get_post_tbl(Z, post_pattern="siopost123"):
        # post_pattern must exist in apps-controllers
        scheme = "https" if Z.certfile and Z.keyfile else "http"
        
        post_prefix = f"{scheme}://{Z.host}:{Z.port}/"

        maybe = {
            x.split("/")[0]: x.split("/")[1]
            for x in Z.handl.routes.keys()
            if post_pattern in x
        }
        post_to = {k: post_prefix + k + "/" + v for k, v in maybe.items()}

        if post_to:
            Z.out_dbg(f"{post_to}")
            return post_to

        sys.exit(f"stop! can not find app with controller {post_pattern}")

    def get_red_param(Z, vars_pattern="SIO_RED_PARAM"):
        # vars_pattern must exist in apps-controllers
        apps_modules = [
            sys.modules[name]
            for name in set(sys.modules)
            if any([e in name for e in Z.post_to.keys()])
        ]

        for mod in apps_modules:
            for var_name, var_value in vars(mod).items():
                if var_name == vars_pattern:
                    Z.out_dbg(f"{vars_pattern} {var_value}")
                    return var_value
        sys.exit(f"stop! can not find app with {vars_pattern}")

    def setup(Z):
        Z.post_to = Z.get_post_tbl()
        Z.red_param = Z.get_red_param()
        # Z.sio = socketio.AsyncServer(async_mode="tornado")
        r_mgr = socketio.AsyncRedisManager(
            Z.red_param[0], channel=Z.red_param[1], write_only=False
        )

        Z.sio = socketio.AsyncServer(
            async_mode=Z.sio_mode, #"tornado",
            client_manager=r_mgr,
            cors_allowed_origins="*",
            # SameSite=None,
            # logger=True,
            # engineio_logger=True,
        )

    def out_dbg(Z, data, color="yellow", to_file=True):
        if to_file == False:
            Z.dbg and Z.cprint(data, color)
        else:    
            Z.log_info(f"log_info: {data}")

    def log_info(Z, data):
        Z.log and Z.log.info(data)

    async def db_run( Z, sid, e_name, data={"from": "db_run"},):
        return await Z.post_dispatcher( sid, e_name, data,)

    async def ctrl_emit( Z, sid, e_name, data={"from": "ctrl_emit"},):
        return await Z.post_dispatcher( sid, e_name, data,)

    async def ctrl_call_mult( Z, sid, e_name, data={"from": "ctrl_call_mult"},):
        return await Z.post_dispatcher( sid, e_name, data,)

    # https://blog.jonlu.ca/posts/async-python-http
    async def post_dispatcher( Z, sid, event_name="unk", data=None,):

        async with Z.sio.session(sid) as session:
           try:
               sid_data = session[sid] 
               sid_data["event_name"] = event_name
               sid_data["data"] = data
               post_url = Z.post_to[sid_data["app_nm"]]
           except KeyError:
               Z.log_info(f"post_dispatcher: bad sid={sid}")
               return f"sid {sid} not found in session!"

        async with httpx.AsyncClient(verify=False) as p4w:
            r = await p4w.post( post_url, json=sid_data,)
            r.status_code != 200 and Z.log_info( f"post_dispatcher: {post_url} {r.status_code}")
            return r.text

        # https://www.tornadoweb.org/en/stable/guide/coroutines.html        

def torMig():
    # ------------------------------------------------------------------------------
    import tornado, tornado.web, uvloop

    class Favicon_ico(tornado.web.RequestHandler):
        def get(self):
            self.write(";)")

    class TornadoMig(ServerAdapter):
        import tornado.wsgi, tornado.web, tornado.httpserver

        def __init__(ZZ, *ar, **kw):
            super().__init__(*ar, **kw) 

            ZZ.certfile =  ZZ.options.get("certfile", None) 
            ZZ.keyfile =  ZZ.options.get("keyfile", None) 

            ZZ.client_count = 0
            ZZ.a_count = 0
            ZZ.b_count = 0

        def run(ZZ, py4web_apps_handler):
            ZZ.log = None
            if not ZZ.quiet:
                logging_conf( ZZ.options["logging_level"],)
                ZZ.log = logging.getLogger("mig")
                ZZ.log.propagate = True

            s_app = MultiSio( py4web_apps_handler, host = ZZ.host, port = ZZ.port, 
                              certfile=ZZ.certfile, keyfile=ZZ.keyfile,
                              log= ZZ.log, sio_mode = 'tornado')
            sio = s_app.sio

            async def period_task(sid):
                e_name = sys._getframe().f_code.co_name
                count = 0
                while True:
                    async with sio.session(sid) as session:
                       if not sid in session:
                           break
                    count += 1
                    await sio.emit( "my_response", { "data": f"period_task 7-sec-counter-to-all {count} to {sid}  " },)
                    await sio.sleep(7)

            async def debug_task(sid):
                e_name = sys._getframe().f_code.co_name
                count = 0
                while True:
                    async with sio.session(sid) as session:
                       if not sid in session:
                           break
                    count += 1
                    await s_app.ctrl_emit( sid, "ctrl_emit", data={"orig_e": e_name, "bcast": False},)
                    await s_app.ctrl_emit( sid, "xxx_cmd", data={"sid": sid, "count": count})
                    await s_app.post_dispatcher( sid, e_name, data={"sid": sid, "count": count})
                    s_app.out_dbg( f"================= client_count: {ZZ.client_count}", "cyan",)
                    await sio.sleep(10)


            async def simple_task(sid):
                e_name = sys._getframe().f_code.co_name
                am = random.randint(1, 9)
                bm = random.randint(1, 9)
                await sio.sleep(5)

                try:
                    result = await sio.call("mult", {"numbers": [am, bm]}, to=sid)
                    s_app.log_info(f"result from js-mult: {result}")
                except socketio.exceptions.TimeoutError: #asyncio.TimeoutError:
                    s_app.out_dbg(f"------------------ timeout error on js-mult {e_name}")

                try:
                    r = await s_app.ctrl_call_mult( sid, "ctrl_call_mult", data={"numbers": [am, bm]},)
                except socketio.exceptions.TimeoutError: #asyncio.TimeoutError:
                    s_app.log_info(f"timeout error on {e_name} ctrl_call_mult")

                s_app.out_dbg(f"+++++++++++++++++ {r}")

            @sio.event
            async def close_room(sid, message):
                e_name = sys._getframe().f_code.co_name
                await sio.emit( "my_response", {"data": "Room " + message["room"] + " is closing."}, room=message["room"],)
                await sio.close_room(message["room"])

            @sio.event
            async def connect( sid, environ,):
                e_name = sys._getframe().f_code.co_name

                url, ctrl_nm, app_nm = None, None, None

                try:
                    url = environ["HTTP_REFERER"]
                except KeyError:
                    url = environ["HTTP_ORIGIN"]
                    s_app.log_info(f"bad url {url}")
                    return False

                url_items = url.rsplit("/")
                app_nm = url_items[3] if len(url_items) >= 4 else None
                if not app_nm in s_app.post_to:  # Z.p4w_apps_names:
                    s_app.log_info(f"bad app_nm: {app_nm}")
                    return False

                ctrl_nm = url_items[4] if len(url_items) >= 5 else None

                username = environ.get("HTTP_X_USERNAME")
                s_app.log_info(f"HTTP_X_USERNAME: {username} {app_nm}")
                if not username:
                    # raise ConnectionRefusedError('authentication failed')
                    return False
                    # session["qu"] = asyncio.Queue()
                await sio.emit("user_joined", f"{username} sid: {sid}")

                # end auth etc

                ZZ.client_count += 1
                s_app.log_info(f"{sid} connected")

                myroom = None
                if random.random() > 0.5:
                    sio.enter_room(sid, "a")
                    myroom = "a"
                    ZZ.a_count += 1
                    await sio.emit("room_count", ZZ.a_count, to="a")
                else:
                    sio.enter_room(sid, "b")
                    myroom = "b"
                    ZZ.b_count += 1
                    await sio.emit("room_count", ZZ.b_count, to="b")

                async with sio.session(sid) as session:
                    session[sid] = { 
                        "sid": sid, 
                        "app_nm": app_nm,
                        "ctrl_nm": ctrl_nm,
                        "username": username,
                        "room": myroom,
                    }

                await s_app.db_run( sid, "db_run", data={ "cmd": "PUT", "table": "sio_log", 
                    "inout": "in", "orig_e": e_name, "app_nm": app_nm, "ctrl_nm": ctrl_nm},)

                await sio.emit( "client_count", f"{ZZ.client_count}",)

                sio.start_background_task(simple_task, sid)
                sio.start_background_task(period_task, sid)
                sio.start_background_task(debug_task, sid)

                await s_app.post_dispatcher( sid, e_name,)

            @sio.event
            async def disconnect_request(sid):
                e_name = sys._getframe().f_code.co_name
                await sio.disconnect(sid)

            @sio.event
            async def disconnect(sid):
                e_name = sys._getframe().f_code.co_name

                async with sio.session(sid) as session:
                    if not sid in session:
                        return

                ar = random.randint(1, 9)
                br = random.randint(1, 9)

                await s_app.db_run( sid, "db_run", data={ "cmd": "PUT", "table": "sio_log", 
                    "inout": "out", "orig_e": e_name, },)

                #await s_app.db_run( sid, "db_run", data={ "cmd": "PUT", "table": "sio_data", 
                #    "counter": ['hello', 'world', ar, {'counter': br}], "orig_e": e_name, },)

                #await s_app.db_run( sid, "db_run", data={ "cmd": "PUT", "table": "sio_data", 
                #    "counter":  {'counter': br}, "orig_e": e_name, },)

                await s_app.db_run( sid, "db_run", data={ "cmd": "PUT", "table": "sio_data", 
                    "counter": br, "orig_e": e_name, },)

                #await s_app.db_run( sid, "db_run", data={ "cmd": "UPDATE", "table": "sio_log", 
                #    "id": 12, "inout": "----", "orig_e": '+++++', },)

                #r = await s_app.db_run( sid, "db_run", data={ "cmd": "GET", "table": "sio_log", "id": 1 } )
                #s_app.out_dbg (f"{r}", 'cyan')

                r = await s_app.db_run( sid, "db_run", data={ "cmd": "GET", "table": "sio_data", "id": 1 } )
                #s_app.out_dbg (type(r))
                #s_app.out_dbg (f"{r}!!!!!", 'cyan')
                s_app.out_dbg (json.loads(r)[0])

                #await s_app.db_run( sid, "db_run", data={ "cmd": "DEL", "table": "sio_log", "id": 7 } )

                ZZ.client_count -= 1
                s_app.log_info(f"{sid} disconnected")
                await sio.emit("client_count", ZZ.client_count)
                if "a" in sio.rooms(sid):
                    ZZ.a_count -= 1
                    await sio.emit("room_count", ZZ.a_count, to="a")
                else:
                    ZZ.b_count -= 1
                    await sio.emit("room_count", ZZ.b_count, to="b")

                async with sio.session(sid) as session:
                    if sid in session:
                        await sio.emit("user_left", session[sid]["username"])

                async with sio.session(sid) as session:
                    del session[sid] 

            @sio.event
            async def sum(sid, data):
                e_name = sys._getframe().f_code.co_name
                # Z.log and Z.log.info(data)
                result = data["numbers"][0] + data["numbers"][1]
                return {"result": result, "event_name": e_name}

            @sio.on("*")
            async def catch_all(event, sid, data):
                e_name = sys._getframe().f_code.co_name
                s_app.out_dbg(f"----------------------- {e_name}: {event} {data}")
                # https://python-socketio.readthedocs.io/en/latest/server.html#defining-event-handlers

            async def main():
                wsgi_box = tornado.wsgi.WSGIContainer(py4web_apps_handler)

                app = tornado.web.Application(
                    [
                        #(r'/favicon.ico', tornado.web.StaticFileHandler, {"path": ""}),
                        (r"/favicon.ico", Favicon_ico),
                        (r"/socket.io/", socketio.get_tornado_handler ( s_app.sio) ),
                        (r".*", tornado.web.FallbackHandler, dict(fallback=wsgi_box)),
                    ],
                )

                ssl_ctx = None

                if ZZ.certfile and ZZ.keyfile:
                    ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                    ssl_ctx.load_cert_chain(ZZ.certfile, ZZ.keyfile)

                server = tornado.httpserver.HTTPServer(app, ssl_options=ssl_ctx)

                server.listen(port=ZZ.port, address=ZZ.host)
                await asyncio.Event().wait()

            if sys.version_info >= (3, 11):
                with asyncio.Runner(loop_factory=uvloop.new_event_loop) as runner:
                    runner.run(main())
            else:
                uvloop.install()
                asyncio.run(main())

    return TornadoMig


# ---------------------- aiohttp + socketio -----------------------------------------------------

# pip install aiohttp
# pip install aiohttp_wsgi


# import socketio, httpx, asyncio, json, random, sys
# ---------------------------------------------------------
# https://github.com/miguelgrinberg/python-socketio/issues/142
# https://github.com/miguelgrinberg/python-socketio/issues/461
# https://github.com/miguelgrinberg/python-socketio/issues/1101

class MigNsp(socketio.AsyncNamespace,):
    def __init__(self, *ar, **kw):
         super().__init__(*ar, )

         self.s_app=kw['k_app']
         self.sio=self.s_app.sio #kw['k_sio']

         self.client_count = 0
         self.a_count = 0
         self.b_count = 0

    async def debug_task(self, sid):
        e_name = sys._getframe().f_code.co_name
        count = 0
        while True:

            async with self.sio.session(sid) as session:
                if not sid in session:
                    break
    
            count += 1
            await self.s_app.ctrl_emit( sid, "ctrl_emit", data={"orig_e": e_name, "bcast": False},)
            await self.s_app.ctrl_emit( sid, "xxx_cmd", data={"sid": sid, "count": count})
            await self.s_app.post_dispatcher( sid, e_name, data={"sid": sid, "count": count})
            self.s_app.out_dbg( f"================= self.client_count: {self.client_count}", "cyan",)
            await self.sio.sleep(10)

    async def period_task(self, sid):
        e_name = sys._getframe().f_code.co_name
        count = 0
        while True:
            async with self.sio.session(sid) as session:
                if not sid in session:
                    break
            count += 1
            await self.sio.emit( "my_response", { "data": f"period_task 7-sec-counter-to-all {count} to {sid}  " },)
            await self.sio.sleep(7)
    
    async def simple_task(self, sid):
        e_name = sys._getframe().f_code.co_name
        am = random.randint(1, 9)
        bm = random.randint(1, 9)
        await self.sio.sleep(5)
    
        try:
            result = await self.sio.call("mult", {"numbers": [am, bm]}, to=sid)
            self.s_app.log_info(f"result from js-mult: {result}")
        except socketio.exceptions.TimeoutError:
            self.s_app.out_dbg(f"------------------ timeout error on js-mult {e_name}")
    
        try:
            r = await self.s_app.ctrl_call_mult( sid, "ctrl_call_mult", data={"numbers": [am, bm]},)
        except socketio.exceptions.TimeoutError:
            self.s_app.log_info(f"timeout error on {e_name} ctrl_call_mult")
    
        self.s_app.out_dbg(f"+++++++++++++++++ {r}")
       
    
    async def on_close_room(self, sid, message):
        e_name = sys._getframe().f_code.co_name
        await self.sio.emit( "my_response", {"data": "Room " + message["room"] + " is closing."}, room=message["room"],)
        await self.sio.close_room(message["room"])
    
    async def on_connect(self, sid, environ,):
        e_name = sys._getframe().f_code.co_name
    
        url, ctrl_nm, app_nm = None, None, None
    
        try:
            url = environ["HTTP_REFERER"]
        except KeyError:
            url = environ["HTTP_ORIGIN"]
            self.s_app.log_info(f"bad url {url}")
            return False
    
        url_items = url.rsplit("/")
        app_nm = url_items[3] if len(url_items) >= 4 else None
        if not app_nm in self.s_app.post_to:  # Z.p4w_apps_names:
            self.s_app.log_info(f"bad app_nm: {app_nm}")
            return False
    
        ctrl_nm = url_items[4] if len(url_items) >= 5 else None
    
        username = environ.get("HTTP_X_USERNAME")
        self.s_app.log_info(f"HTTP_X_USERNAME: {username} {app_nm}")
        if not username:
            # raise ConnectionRefusedError('authentication failed')
            return False

        await self.sio.emit("user_joined", f"{username} sid: {sid}")
    
        # end auth etc
    
        self.client_count += 1
        self.s_app.log_info(f"{sid} connected")
    
        myroom = None
        if random.random() > 0.5:
            self.sio.enter_room(sid, "a")
            myroom = "a"
            self.a_count += 1
            await self.sio.emit("room_count", self.a_count, to="a")
        else:
            self.sio.enter_room(sid, "b")
            myroom = "b"
            self.b_count += 1
            await self.sio.emit("room_count", self.b_count, to="b")
    
        async with self.sio.session(sid) as session:
            session[sid] = { 
                "sid": sid, 
                "app_nm": app_nm,
                "ctrl_nm": ctrl_nm,
                "username": username,
                "room": myroom,
                }
    
        await self.s_app.db_run( sid, "db_run", data={ "cmd": "PUT", "table": "sio_log", 
            "inout": "in", "orig_e": e_name, "app_nm": app_nm, "ctrl_nm": ctrl_nm},)
    
        await self.sio.emit( "client_count", f"{self.client_count}",)
    
        self.sio.start_background_task(self.simple_task, sid)
        self.sio.start_background_task(self.period_task, sid)
        self.sio.start_background_task(self.debug_task, sid)
    
        await self.s_app.post_dispatcher( sid, e_name,)
    
    async def on_disconnect_request(self, sid):
        e_name = sys._getframe().f_code.co_name
        await self.sio.disconnect(sid)
    
    async def on_disconnect(self, sid):
        e_name = sys._getframe().f_code.co_name
    
        async with self.sio.session(sid) as session:
            if not sid in session:
                return
    
        ar = random.randint(1, 9)
        br = random.randint(1, 9)
    
        await self.s_app.db_run( sid, "db_run", data={ "cmd": "PUT", "table": "sio_log", 
            "inout": "out", "orig_e": e_name, },)
    
        #await self.s_app.db_run( sid, "db_run", data={ "cmd": "PUT", "table": "sio_data", 
        #    "counter": ['hello', 'world', ar, {'counter': br}], "orig_e": e_name, },)
    
        #await self.s_app.db_run( sid, "db_run", data={ "cmd": "PUT", "table": "sio_data", 
        #    "counter":  {'counter': br}, "orig_e": e_name, },)
    
        await self.s_app.db_run( sid, "db_run", data={ "cmd": "PUT", "table": "sio_data", 
            "counter": br, "orig_e": e_name, },)
    
        #await self.s_app.db_run( sid, "db_run", data={ "cmd": "UPDATE", "table": "sio_log", 
        #    "id": 12, "inout": "----", "orig_e": '+++++', },)
    
        #r = await self.s_app.db_run( sid, "db_run", data={ "cmd": "GET", "table": "sio_log", "id": 1 } )
        #self.s_app.out_dbg (f"{r}", 'cyan')
    
        r = await self.s_app.db_run( sid, "db_run", data={ "cmd": "GET", "table": "sio_data", "id": 1 } )
        #self.s_app.out_dbg (type(r))
        #self.s_app.out_dbg (f"{r}!!!!!", 'cyan')
        self.s_app.out_dbg (json.loads(r)[0])
    
        #await self.s_app.db_run( sid, "db_run", data={ "cmd": "DEL", "table": "sio_log", "id": 7 } )
    
        self.client_count -= 1
        self.s_app.log_info(f"{sid} disconnected")
        await self.sio.emit("client_count", self.client_count)
        if "a" in self.sio.rooms(sid):
            self.a_count -= 1
            await self.sio.emit("room_count", self.a_count, to="a")
        else:
            self.b_count -= 1
            await self.sio.emit("room_count", self.b_count, to="b")
    
        async with self.sio.session(sid) as session:
            await self.sio.emit("user_left", session[sid]["username"])

        async with self.sio.session(sid) as session:
            del session[sid] 
    
    async def on_sum(self, sid, data):
        e_name = sys._getframe().f_code.co_name
        # Z.log and Z.log.info(data)
        result = data["numbers"][0] + data["numbers"][1]
        return {"result": result, "event_name": e_name}
    
    async def on_catch_all(event, sid, data):
        e_name = sys._getframe().f_code.co_name
        self.s_app.out_dbg(f"----------------------- {e_name}: {event} {data}")
    #    # https://python-socketio.readthedocs.io/en/latest/server.html#defining-event-handlers


    # ---------------------------------------------------------

def aioMig():
    from aiohttp import web
    from aiohttp_wsgi import WSGIHandler  # pip install aiohttp_wsgi

    class AioSio(ServerAdapter):

        def __init__(self, *ar, **kw):
            super().__init__(*ar, **kw)

            self.certfile =  self.options.get("certfile", None)
            self.keyfile =  self.options.get("keyfile", None)

        async def favicon_ico(self,request):
            return web.Response( text=';)', content_type='text/plain')

        async def robots_txt(self,request):
            return web.Response( text=';(', content_type='text/plain')

        def run(self, py4web_apps_handler):
            self.log= None
            if not self.quiet:
                self.log = logging_conf( self.options["logging_level"], "aiohttp"  )
            
            s_app = MultiSio( py4web_apps_handler, host = self.host, port = self.port, 
                    certfile=self.certfile, keyfile=self.keyfile,
                    log= self.log, sio_mode="aiohttp")

            sio = s_app.sio

            sio.register_namespace(MigNsp('/', k_app=s_app, k_sio=sio))

            wsgi_box = WSGIHandler(py4web_apps_handler)
            aio_app = web.Application()

            sio.attach( aio_app)

            ssl_ctx = None 
            if self.certfile and self.keyfile:
                ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                ssl_ctx.load_cert_chain(certfile=self.certfile, keyfile=self.keyfile)

            aio_app.router.add_routes([web.get("/favicon.ico", self.favicon_ico )])
            aio_app.router.add_routes([web.get("/robots.txt", self.robots_txt )])
            aio_app.router.add_route("*", "/{path_info:.*}", wsgi_box)

            web.run_app(aio_app, host=self.host, port=self.port , ssl_context = ssl_ctx )

    return AioSio

# https://stackoverflow.com/questions/54165443/how-to-return-html-response-from-aiohttp-web-server
# curl -k "http://192.168.1.161:9000/socket.io/?EIO=4&transport=polling"


# https://stackoverflow.com/questions/63528951/how-to-make-a-logging-handler-log-to-flask-socketio
# https://medium.com/the-research-nest/how-to-log-data-in-real-time-on-a-web-page-using-flask-socketio-in-python-fb55f9dad100
# https://github.com/donskytech/python-flask-socketio
# https://github.com/ryanbekabe/Python_Socket.io
# https://github.com/lareii/flask-socketio-chat
# http://blog.dataroadtech.com/asynchronous-task-execution-with-flask-celery-and-socketio/


# https://github.com/kasullian/ChatIO/blob/main/server.py
# https://stackoverflow.com/questions/60266397/using-multiple-asyncio-queues-effectively
# https://stackoverflow.com/questions/58408980/python-socket-io-emit-call-from-function
# https://stackoverflow.com/questions/71338054/python-send-data-every-10-seconds-via-socket-io
# sio.get_sid(namespace='/my-namespace')
# sio.get_sid() https://stackoverflow.com/questions/66160701/how-to-synchronize-socket-sid-on-server-and-client

# https://meejah.ca/blog/python3-twisted-and-asyncio
# https://github.com/meejah/txtorcon/blob/master/examples/web_onion_service_aiohttp.py

"""
# how to write to server-py4web.log from controllers.py
#
# controllers.py


import sys
import logging
from .common import logger
from .settings import APP_NAME
from threading import Lock

print (logger.level)

def set_color(org_string, level=None):
    color_levels = {
        10: "\033[36m{}\033[0m",       # DEBUG
        20: "\033[32m{}\033[0m",       # INFO
        30: "\033[33m{}\033[0m",       # WARNING
        40: "\033[31m{}\033[0m",       # ERROR
        50: "\033[7;31;31m{}\033[0m"   # FATAL/CRITICAL/EXCEPTION
    }
    if level is None:
        return color_levels[20].format(str(org_string))
    else:
        return color_levels[int(level)].formatstr((org_string))

logger.info(set_color("test"))
logger.debug(set_color("test", level=10))
logger.warning(set_color("test", level=30))
logger.error(set_color("test", level=40))
logger.fatal(set_color("test", level=50))

_srv_log=None

def log_info(mess, dbg=True, ):
    def salog(pat='SA:'):
        global _srv_log
        if _srv_log and isinstance( _srv_log, logging.Logger ):
           return _srv_log
        hs= [e for e in logging.root.manager.loggerDict if e.startswith(pat) ]
        if len(hs) == 0:
            return logger

        _sa_lock = Lock() 
        with _sa_lock:
            _srv_log = logging.getLogger(hs[0])

        return _srv_log

    dbg and salog().info(str(mess))

log_warn=log_info
log_debug=log_info

log_warn('0'* 30 + ' ' +APP_NAME)

@action('index')
@action.uses('index.html', auth, T, )
def index():
    # curl -k -I  https://192.168.1.161:9000/mig1ssl/index

    log_warn('7'* 30 + ' ' +APP_NAME)
    log_info('9'* 30 + ' ' +APP_NAME)

"""

"""
httpx
gevent
gevent-ws
python-socketio
asyncio
aiohttp
aiohttp_wsgi
uvloop
black
faker
redis[hiredis]
celery
Pillow
codetiming
"""
