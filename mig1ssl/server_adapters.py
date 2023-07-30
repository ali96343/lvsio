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

def logging_conf(level, log_file="server-py4web.log" ):
    log_to = dict()
    # export PY4WEB_LOGS=/tmp # export PY4WEB_LOGS=
    log_dir = os.environ.get('PY4WEB_LOGS', None)
    if log_dir:
        path_log_file = os.path.join( log_dir, log_file )
        log_to = { "filename": path_log_file, "filemode": "w", } 
        print (f"PY4WEB_LOGS={log_dir}, open {path_log_file}")

    _short="%(message)s"
    _long="%(asctime)s | %(threadName)s | %(message)s | (%(filename)s:%(lineno)d)"

    logging.basicConfig(
        format=_short,
        encoding="utf-8",
        level=check_level( level ) ,
        **log_to,
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
                log_dir = os.environ.get('PY4WEB_LOGS', None)
                fh = logging.FileHandler() if not log_dir else (
                       logging.FileHandler( os.path.join(log_dir, "server-py4web.log") )
                       )
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
                    ca_certs=None,
                    ciphers=None,
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
        def run(self, app):
            self.log = None

            if not self.quiet:
                logging_conf(
                    self.options["logging_level"],
                )
                self.log = logging.getLogger("WSGIRef")
                self.log.addHandler(logging.StreamHandler())

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

            #handler_cls =  self.options.get("handler_class", LogHandler)
            server_cls = Server

            if ":" in self.host:  # Fix wsgiref for IPv6 addresses.
                if getattr(server_cls, "address_family") == socket.AF_INET:

                    class server_cls(server_cls):
                        address_family = socket.AF_INET6

            srv = make_server(self.host, self.port, app, server_cls, LogHandler )
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
        def run(self, handler):
            if not self.quiet:
                logging_conf( self.options["logging_level"],)
                log = logging.getLogger("Pyruvate")
                log.addHandler(logging.StreamHandler())

            pyruvate.serve( handler, f"{self.host}:{self.port}", get_workers(self.options, default=10),)

    return srvPyruvate


# --------------------------------------- Mig --------------------------------
# alias mig3="cd $p4w_path && ./py4web.py  run apps -s tornadoMig --ssl_cert=cert.pem --ssl_key=key.pem -H 192.168.1.161 -P 9000 -L 20"

# version 0.0.5

def tornadoMig():
    #  curl -k "http://127.0.0.1:8000/socket.io/?EIO=4&transport=polling"

    import socketio, httpx

    class sio_apps_init:
        # Z == self, mypep ;)
        def __init__(Z, P, handl, debug = True):
            Z.P = P
            Z.log = P.log
            Z.handl = handl
            Z.debug = debug
            Z.sids_connected = dict()
            Z.sio = None
            Z.post_to = None
            Z.red_param = None, None

        def cprint(Z, mess="mess", color="green"):
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
            print(c_fmt.format(mess))
            return mess            

        def get_post_tbl(Z, post_pattern = "siopost123"):
            # post_pattern must exist in apps-controllers
            scheme = "https" if Z.P.options.get("certfile", None) and Z.P.options.get("keyfile", None) else "http"
            post_prefix = f"{scheme}://{Z.P.host}:{Z.P.port}/"
        
            maybe =  { x.split("/")[0]: x.split("/")[1] for x in Z.handl.routes.keys() if post_pattern in x }
            post_to = { k: post_prefix + k + '/' + v  for k,v in maybe.items() }
        
            if post_to:
                Z.out_dbg (f"{post_to}")
                return post_to
        
            sys.exit (f'stop! can not find app with controller {post_pattern}')

        
        def get_red_vars(Z, vars_pattern="SIO_RED_PARAM"):
            # vars_pattern must exist in apps-controllers
            apps_modules = [sys.modules[name] for name in set( sys.modules ) if any (
                             [ e in name for e in Z.post_to.keys() ] )]
        
            for mod in apps_modules:
                for var_name, var_value in vars(mod).items():
                    if var_name == vars_pattern:
                        Z.out_dbg (f"{vars_pattern} {var_value}")
                        return var_value
            sys.exit (f'stop! can not find app with {vars_pattern}')

        @property
        def get_sio(Z):
            Z.post_to = Z.get_post_tbl()
            Z.red_param = Z.get_red_vars()
            #Z.sio = socketio.AsyncServer(async_mode="tornado")
            r_mgr = socketio.AsyncRedisManager( Z.red_param[0], channel=Z.red_param[1], write_only=False)

            Z.sio = socketio.AsyncServer(
                async_mode="tornado",
                client_manager=r_mgr,
                cors_allowed_origins="*",
                # SameSite=None,
                # logger=True,
                # engineio_logger=True,
            )

            return Z.sio 

        @property
        def get_handl(Z):
            return socketio.get_tornado_handler(Z.sio) 

        def out_dbg(Z, data, color='yellow'):
            Z.debug and Z.cprint(data, color)

        def log_info(Z, data):
            Z.log and Z.log.info(data)

        async def db_run(Z, sid, e_name ,  data={'from':'db_run'},  ):    
            await Z.run_controller( sid, e_name, data, )
            #Z.log and Z.log.info(data)

        async def ctrl_emit(Z, sid, e_name ,  data={'from':'ctrl_emit'}, ):    
            await Z.run_controller( sid, e_name, data, )

        async def ctrl_call_mult(Z, sid, e_name ,  data={'from':'ctrl_call_mult'}, ):    
            r = await Z.run_controller( sid, e_name, data, )
            return r

        async def run_controller( Z, sid, event_name='unk', data=None, ):

            try:
                sid_data = Z.sids_connected[sid]
                sid_data['event_name'] = event_name 
                sid_data['data'] = data
                post_url = Z.post_to[ sid_data["app_nm"]  ]
            except KeyError:
                Z.log_info(f"run_controller bad sid={sid}")
                return f"sid {sid} not found in sids_connected!"

            async with httpx.AsyncClient( verify=False) as p4w:
                r = await p4w.post( post_url, json=sid_data, )
                r.status_code != 200 and Z.log_info( f"httpx.AsyncClient: {post_url} {r.status_code}")
                return r
                #Z.out_dbg(f"+++++++++++++++++ {r.text}" )

    # ------------------------------------------------------------------------------
    import tornado, asyncio, uvloop, random

    class TornadoMig(ServerAdapter):
        import tornado.wsgi, tornado.web, tornado.httpserver 

        def run(ZZ, handler):  

            ZZ.log = None
            if not ZZ.quiet:
                logging_conf( ZZ.options["logging_level"],)
                ZZ.log = logging.getLogger("tornadoMig")
                ZZ.log.addHandler(logging.StreamHandler())
            
            s_app = sio_apps_init(ZZ, handler, )
            sio = s_app.get_sio

            ZZ.client_count = 0
            ZZ.a_count = 0
            ZZ.b_count = 0

            async def period_task(sid):
                #return False
                e_name = sys._getframe().f_code.co_name
                count = 0
                while True:
                    if not sid in s_app.sids_connected: 
                        break

                    count += 1

                    await sio.emit( "my_response", {"data": f"period_task 7-sec-counter-to-all {count} to {sid}  "},)
                    
                    await s_app.ctrl_emit( sid, 'ctrl_emit', 
                             data={ 'orig_e': e_name, 'event_to': 'some_event', 'sid_to': None, 'bcast':False  } , 
                              )

                    await s_app.ctrl_emit( sid, 'XXX_cmd', data={"cmd": "cmd",  
                              "cmd_args": "cmd_args", "sid": sid, "count": count } )

                    await s_app.run_controller( sid, e_name, data={"cmd": "cmd", 
                              "cmd_args": "cmd_args", "sid": sid, "count": count } )
                    
                    await s_app.db_run( sid, 'db_run', data={ 'orig_e': e_name, 'event_to': 'some_event', 
                        'cmd': 'PUT', 'table': 'log_table','id': None,  'log_msg': 'hello, dear', 'red_emit': False,
                        'username': 'unk','sid_to': None, 'bcast':False  }  )
                    
                    await sio.sleep(7)

            async def simple_task(sid):
                e_name = sys._getframe().f_code.co_name
                am = random.randint(1,9)
                bm = random.randint(1,9)
                await sio.sleep(5)
                result = await sio.call("mult", {"numbers": [am, bm]}, to=sid)
                s_app.log_info(f"result from js-mult: {result}")
                res = await s_app.ctrl_call_mult( sid, 'ctrl_call_mult', data={  "numbers": [am, bm]},  )
                s_app.out_dbg(f"+++++++++++++++++ {res.text}" )

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
                    s_app.log_info(f"bad url {url}")
                    return False

                url_items = url.rsplit("/")
                app_nm = url_items[3] if len(url_items) >= 4 else None
                if not app_nm in s_app.post_to: #Z.p4w_apps_names:
                    s_app.log_info(f"bad app_nm: {app_nm}")
                    return False

                func_nm = url_items[4] if len(url_items) >= 5 else None

                username = environ.get("HTTP_X_USERNAME")
                s_app.log_info(f"HTTP_X_USERNAME: {username} {app_nm}")
                if not username:
                    # raise ConnectionRefusedError('authentication failed')
                    return False
                async with sio.session(sid) as session:
                    session["username"] = username
                    #session["qu"] = asyncio.Queue()
                await sio.emit("user_joined", f"{username} sid: {sid}")
                await s_app.db_run( sid, 'db_run', data={ 'orig_e': e_name, 'event_to': 'some_event', 
                            'username': username,'sid_to': None, 'bcast':False  }  )

                # end auth etc

                ZZ.client_count += 1
                s_app.log_info(f"{sid} connected")

                myroom= None
                if random.random() > 0.5:
                    sio.enter_room(sid, "a")
                    myroom="a"
                    ZZ.a_count += 1
                    await sio.emit("room_count", ZZ.a_count, to="a")
                else:
                    sio.enter_room(sid, "b")
                    myroom="b"
                    ZZ.b_count += 1
                    await sio.emit("room_count", ZZ.b_count, to="b")

                s_app.sids_connected[sid] = { "sid": sid, "app_nm": app_nm, 
                        "func": func_nm, "username": username, "room": myroom}

                await sio.emit("client_count", f"{ZZ.client_count} {set(s_app.sids_connected.keys())}")

                sio.start_background_task(simple_task, sid)
                sio.start_background_task(period_task, sid)

                await s_app.run_controller(sid, e_name, )

            @sio.event
            async def disconnect_request(sid):
                e_name = sys._getframe().f_code.co_name
                await sio.disconnect(sid)
                
            @sio.event
            async def disconnect(sid):
                e_name = sys._getframe().f_code.co_name

                if not sid in s_app.sids_connected: 
                    return

                del s_app.sids_connected[sid]

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
                    await sio.emit("user_left", session["username"])
            
            @sio.event
            async def sum(sid, data):
                e_name = sys._getframe().f_code.co_name
                #Z.log and Z.log.info(data)
                result = data['numbers'][0] + data['numbers'][1]
                return {'result': result, 'event_name': e_name}

            @sio.on('*')
            async def catch_all(event, sid, data):
                e_name = sys._getframe().f_code.co_name
                s_app.out_dbg(f'----------------------- {e_name}: {event} {data}')
                # https://python-socketio.readthedocs.io/en/latest/server.html#defining-event-handlers

        
            async def main():
                container = tornado.wsgi.WSGIContainer(handler)

                app = tornado.web.Application(
                    [
                        (r"/socket.io/", s_app.get_handl),
                        (r".*", tornado.web.FallbackHandler, dict(fallback=container)),
                    ],
                )

                ssl_ctx, certfile, keyfile = None, ZZ.options.get("certfile", None), ZZ.options.get("keyfile", None)
                if certfile and keyfile:
                    ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                    ssl_ctx.load_cert_chain(certfile, keyfile)

                server = tornado.httpserver.HTTPServer(app, ssl_options=ssl_ctx )

                server.listen(port=ZZ.port, address=ZZ.host)
                await asyncio.Event().wait()

            if sys.version_info >= (3, 11):
                with asyncio.Runner(loop_factory=uvloop.new_event_loop) as runner:
                    runner.run(main())
            else:
                uvloop.install()
                asyncio.run(main())

    return TornadoMig

# https://github.com/kasullian/ChatIO/blob/main/server.py
# https://stackoverflow.com/questions/60266397/using-multiple-asyncio-queues-effectively
# https://stackoverflow.com/questions/58408980/python-socket-io-emit-call-from-function
# https://stackoverflow.com/questions/71338054/python-send-data-every-10-seconds-via-socket-io
# sio.get_sid(namespace='/my-namespace')
# sio.get_sid() https://stackoverflow.com/questions/66160701/how-to-synchronize-socket-sid-on-server-and-client


