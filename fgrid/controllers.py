from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
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
from pydal.tools.tags import Tags

from py4web.utils.factories import Inject
from py4web.utils.url_signer import URLSigner

from .models import grps, x_groups, x_permissions

try:
    from .left_menu import l_menu
except ImportError:
    l_menu = []


@action("index")
@action.uses("index.html", auth, T)
def index():
    user = auth.get_user()
    message = T("index Hello {first_name}".format(**user) if user else "index Hello")
    actions = {"allowed_actions": auth.param.allowed_actions}
    return dict(message=message, actions=actions, l_menu=l_menu)


@action("db_tables")
@action.uses(auth, T, db)
def db_tables():
    return ", ".join(db.tables)


@action("mi2")
def mi2():
    return "its mi2"


@action("mi3")
def mi3():
    return "its mi3"


@action("mi4")
@action.uses("mi4.html", auth, T)
def mi4():
    user = auth.get_user()
    message = T("mi4 Hello {first_name}".format(**user) if user else "mi4 Hello")
    actions = {"allowed_actions": auth.param.allowed_actions}
    return dict(message=message, actions=actions, l_menu=l_menu)


@action("mi5")
@action.uses("mi5.html", auth, T, Inject(l_menu=l_menu))
def mi5():
    user = auth.get_user()
    message = T("mi5 Hello {first_name}".format(**user) if user else "mi5 Hello")
    actions = {"allowed_actions": auth.param.allowed_actions}
    return dict(
        message=message,
        actions=actions,
    )


# ---------------------------------------------------------------
# https://py4web.com/_documentation/static/en/chapter-13.html?highlight=tag
# firefox  http://localhost:8000/dblmenu/find_tag/manager
# curl -H "Accept: application/json"  http://localhost:8000/dblmenu/find_tag/dancer
# curl -H "Accept: application/json"  http://localhost:8000/dblmenu/find_tag/manager
#
# with self-signed ssl
# https://reqbin.com/req/c-bvijc9he/curl-follow-redirect
# alias wassl="cd /home/w3p/set7-py39/py4web && ./py4web.py run apps -s wsgirefThreadingServer  --watch=off --port=8000 --ssl_cert=server.pem"
# curl -k -H "Accept: application/json" http://localhost:8000/dblmenu/find_tag/dancer
# ignore bad-ssl (self-signed cert), follow redirect
#  curl -k -H "Accept: application/json" -L  http://localhost:8000/dblmenu/find_tag/dancer

# print(db.tables)
# print( db(db.auth_user_tag_grps).select() )


@action("find_tag/{group_name}")
@action.uses(db)
def find_tag(group_name):
    users = db(grps.find([group_name])).select(
        orderby=db.auth_user.first_name | db.auth_user.last_name
    )
    return {"users": users}


# ----------------------------------------------------------------
@action("zap")
@action.uses(auth.user)
def zap():
    user = auth.get_user()
    permission = "zap database"
    if db(x_permissions.find(permission))(
        db.auth_group.name.belongs(x_groups.get(user["id"]))
    ).count():
        # zap db
        return "database zapped"
    else:
        return "you do not belong to any group with permission to zap db"
