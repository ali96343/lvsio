import logging, os, sys

from ombott.server_adapters import ServerAdapter

try:
    from .utils.wsservers import *
except ImportError:
    wsservers_list = []

__all__ = [
    "geventWebSocketServer",
    "wsgirefThreadingServer",
    "rocketServer",
    "gevent",
    "waitressPyruvate",
] + wsservers_list


def gevent():
    # basically tihis is the same as ombotts version, but
    # since reload was added as keyword argument that's being passed to the server
    # this was passed as ssl_options to gevent's pywsgi.WSGIServer. This breaks gevent's api
    # Therefor 'reloader' is removed below in the options passed to the server.
    from gevent import pywsgi, local
    import threading

    if not isinstance(threading.local(), local.local):
        msg = "Ombott requires gevent.monkey.patch_all() (before import)"
        raise RuntimeError(msg)

    class GeventServer(ServerAdapter):
        def run(self, handler):
            if not self.quiet:
                self.log = logging.getLogger("gevent")
            options = self.options.copy()
            try:
                # keep only ssl options
                del options["reloader"]
            except:
                pass

            server = pywsgi.WSGIServer((self.host, self.port), handler, **options)
            server.serve_forever()

    return GeventServer


def geventWebSocketServer():
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    from geventwebsocket.logging import create_logger

    class GeventWebSocketServer(ServerAdapter):
        def run(self, handler):
            server = pywsgi.WSGIServer(
                (self.host, self.port),
                handler,
                handler_class=WebSocketHandler,
                **self.options,
            )

            if not self.quiet:
                server.logger = create_logger("geventwebsocket.logging")
                server.logger.setLevel(logging.INFO)
                server.logger.addHandler(logging.StreamHandler())

            server.serve_forever()

    return GeventWebSocketServer


def log_routes(apps_routes, log_file = 'routes-wsgi.txt'):
    try:
        if os.path.isfile(log_file):
             return 
        with open(log_file, 'w') as f:
            f.write( '\n'.join([ v.rule if '\r' in k else ('/' + k )  
                        for k, v in sorted(apps_routes.items()) ]) )
        print (f'wrote {log_file}')
    except OSError as ex:
        sys.exit(ex)


def wsgirefThreadingServer():
    # https://www.electricmonk.nl/log/2016/02/15/multithreaded-dev-web-server-for-the-python-bottle-web-framework/
    import socket, ssl, datetime
    from concurrent.futures import ThreadPoolExecutor  # pip install futures
    from socketserver import ThreadingMixIn
    from wsgiref.simple_server import WSGIRequestHandler, WSGIServer, make_server

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

    class ToLog(object):
        def __init__(self, logger, level):
           self.logger = logger
           self.level = level
           self.linebuf = ''
    
        def write(self, buf):
           for line in buf.rstrip().splitlines():
              self.logger.log(self.level, 'STD:' +  line.rstrip())
    
        def flush(self):
            pass

    class WSGIRefThreadingServer(ServerAdapter):
        def run(self, app):

            if not self.quiet:
                log_routes(app.routes)
                logging.basicConfig(
                    filename="wsgiref.log",
                    format="%(threadName)s | %(message)s",
                    filemode="w",
                    # filemode="a",
                    encoding="utf-8",
                    level=logging.DEBUG,
                )

                self.log = logging.getLogger("WSGIRef")

                # sys.stderr.write = self.log.error
                # sys.stdout.write = self.log.info
                # print('Test to standard out')
                # raise Exception('Test to standard error' )
                sys.stdout = ToLog(self.log, logging.INFO)
                sys.stderr = ToLog(self.log, logging.ERROR)

            self_run = self  # used in inner classes to access options and logger
            class PoolMixIn(ThreadingMixIn):
                def process_request(self, request, client_address):
                    self.pool.submit(
                        self.process_request_thread, request, client_address
                    )

            class ThreadingWSGIServer(PoolMixIn, WSGIServer):
                daemon_threads = True
                pool = ThreadPoolExecutor(max_workers=40)

            class Server:
                __slots__ = ('wsgi_app','handler_cls','listen','port','server')
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
                        os.system( f"[[  $(command -v fuser) ]] && fuser {self.port}/tcp" )
                        sys.exit(ex)

                    # openssl req  -newkey rsa:4096 -new -x509 -keyout server.pem -out server.pem -days 365 -nodes
                    # ./py4web.py run apps -s wsgirefThreadingServer  --watch=off --port=8000 --ssl_cert=server.pem

                    # openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365 \
                    # -subj "/C=RU/ST=Saint Petersburg/O=SPB/OU=Alex Bsk/CN=localhost/emailAddress=ab96343@gmail.com"
                    # ./py4web.py run apps -s wsgirefThreadingServer --watch=off --port=8000 --ssl_cert=cert.pem --ssl_key=key.pem

                    # openssl s_client -showcerts -connect 127.0.0.1:8000

                    certfile = self_run.options.get("certfile", None)

                    if certfile:
                        self.server.socket = Is_Https(
                            socket=self.server.socket,
                            certfile=certfile,
                            keyfile=self_run.options.get("keyfile", None),
                            host=self.listen,
                            port=self.port,
                            # logger=self_run.log,
                        )

                    self.server.serve_forever()

            class FixedHandler(WSGIRequestHandler):
                def address_string(self):  # Prevent reverse DNS lookups please.
                    return self.client_address[0]

                def log_request(*args, **kw):
                    if not self_run.quiet:
                        return WSGIRequestHandler.log_request(*args, **kw)

                def log_message(self, format, *args):
                    if not self_run.quiet:  # and ( not args[1] in ['200','304']):
                        msg = "%s - - [%s] %s" % (
                            self.client_address[0],
                            self.log_date_time_string(),
                            format % args,
                        )
                        self_run.log.info(msg)
                        # sys.stderr.write(msg)

            handler_cls = self.options.get("handler_class", FixedHandler)
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
    import logging.handlers

    class RocketServer(ServerAdapter):
        def run(self, app):
            if not self.quiet:
                log = logging.getLogger("Rocket")
                log.setLevel(logging.INFO)
                log.addHandler(logging.StreamHandler())
            interface = (
                (
                    self.host,
                    self.port,
                    self.options["keyfile"],
                    self.options["certfile"],
                )
                if self.options.get("certfile", None)
                else (self.host, self.port)
            )
            server = Rocket(interface, "wsgi", dict(wsgi_app=app))
            server.start()

    return RocketServer



def waitressPyruvate():

    # https://2020.ploneconf.org/talks/pyruvate-a-reasonably-fast-non-blocking-multithreaded-wsgi-server
    # https://maurits.vanrees.org/weblog/archive/2021/10/thomas-schorr-pyruvate-wsgi-server-status-update
    # https://gitlab.com/tschorr/pyruvate
    # https://pypi.org/project/pyruvate/

    import pyruvate  # pip install pyruvate

    class srvPyruvate(ServerAdapter):
        def run(self, handler):

            if not self.quiet:
                log = logging.getLogger("Pyruvate")
                log.setLevel(logging.DEBUG)
                log.addHandler(logging.StreamHandler())

            workers = 1000  # self.options['workers']
            pyruvate.serve(handler, f"{self.host}:{self.port}", workers)

    return srvPyruvate

