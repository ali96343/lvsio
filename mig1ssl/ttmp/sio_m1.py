import socketio, sys, os

sio_debug = False
sio = socketio.AsyncServer(async_mode="tornado")

sio_handl =  socketio.get_tornado_handler(sio)

@sio.event
async def connect(sid, environ):
    sio_debug and print("sio: connect ", sid)

@sio.event
async def disconnect(sid):
    sio_debug and print("sio: disconnect ", sid)

# -------------------------------------------------------------------------

def setup_sio( red_url, chan  ):

            r_mgr = socketio.AsyncRedisManager( red_url, channel=chan, write_only=False)

            return socketio.AsyncServer(
                async_mode="tornado",
                client_manager=r_mgr,
                cors_allowed_origins="*",
                # SameSite=None,
                # logger=True,
                # engineio_logger=True,
            )



def get_uri_tbl(handl, P, post_pattern = "siopost123"):
    # post_pattern must exist in apps-controllers
    post_scheme = "https" if P.options.get("certfile", None) else "http"
    post_prefix = f"{post_scheme}://{P.host}:{P.port}/"

    maybe =  { x.split("/")[0]: x.split("/")[1] for x in handl.routes.keys() if post_pattern in x }
    post_to = { k: post_prefix + k + '/' + v  for k,v in maybe.items() }

    if post_to:
        print (post_to)
        return post_to

    sys.exit (f'stop! can not find app with controller {post_pattern}')


def get_red_vars(apps_names, vars_pattern="SIO_RED_PARAM"):

    # vars_pattern must exist in apps-controllers
    apps_modules = [sys.modules[name] for name in set( sys.modules ) if any (
                     [ e in name for e in apps_names ] )]

    for mod in apps_modules:
        for var_name, var_value in vars(mod).items():
            if var_name == vars_pattern:
                print (f"{vars_pattern} {var_value}")
                return var_value
    sys.exit (f'stop! can not find app with {vars_pattern}')

def pre_init(handl, P, post_pattern = "siopost123"):
    #print (handl, P)
    #print (P.host, P.port)

    apps = get_uri_tbl(handl, P, post_pattern = "siopost123")
    x = get_red_vars(apps.keys(), vars_pattern="SIO_RED_PARAM")
    setup_sio( x[0], x[1]  )
