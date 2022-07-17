from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .settings import APP_NAME
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


@action("index")
@action.uses("index.html", auth, T)
def index():
    user = auth.get_user()
    message = T("Hello {first_name}".format(**user) if user else "Hello")
    actions = {"allowed_actions": auth.param.allowed_actions}
    return dict(message=message, actions=actions)


import ombott


@ombott.on_route(f"/{APP_NAME}")
def myhook(hook_path=None):
    print(ombott.request.url)

    #if ombott.request.url.startswith("http://"):
    #    loc = ombott.request.url.replace("http://", "https://", 1)
    loc= 'https://google.com'
    raise ombott.HTTPResponse(
            status="301 Redirect",
            headers={"location": loc},
        )
