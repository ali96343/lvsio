from py4web import action, request, abort, redirect, URL
from yatl.helpers import A, DIV, P
from py4web.core import bottle
from .common import (
    db,
    session,
    T,
    cache,
    auth,
    logger,
    authenticated,
    unauthenticated,
    flash,
)


# https://testdriven.io/blog/asynchronous-tasks-with-falcon-and-celery/

sio_serv_url = "http://localhost:3000"

@unauthenticated("index", "index.html")
def index():

    user = auth.get_user()
    message = T("Hello {first_name}".format(**user) if user else "Hello")
    menu = DIV(
        P(":) sio !!!"),
        DIV(A("sync_id", _role="button", _href=URL("sync_id_ctrl"))),
        DIV(A("flask_chat", _role="button", _href=URL("flask_chat"))),
    )
    return dict(message=message, menu=menu)


@action("sync_id_ctrl", method=["GET", "POST"])
@action.uses(db, session, T, "sync_id.html")
def sync_id_ctrl():
    # ctrl_template_url = "\'" + URL('sync_id_ctrl' ) + "\'"
    # const long_task_url = [[=XML( ctrl_template_url ) ]]

    values = {"slider1": 25, "slider2": 0, "counter": 100, 'data_str': ':)'}

    return locals()


@action("flask_chat", method=["GET", "POST"])
@action.uses(db, session, T, "flask_chat.html")
def flask_chat():
    #print("flask_chat")
    return locals()




# --------------------------------------------------------------------------------------
@action("from_uvicorn", method=["GET", "POST"])
def from_uvicorn():
    import json

    def read_body(request):
        if "wsgi.input" in request:
            post_data = request["wsgi.input"].read()
            if isinstance(post_data, bytes):
                return json.loads(post_data)
        return None

    json_data = read_body(request)

    if json_data:
        BROADCAST_SECRET = "123secret"
        event_name = json_data["event_name"]
        room = json_data["room"]
        data = json_data["data"]
        broadcast_secret = json_data["broadcast_secret"]
        if broadcast_secret == BROADCAST_SECRET:
            print("json-post-data: ", json_data)
    return "mig/from_uvicorn"
