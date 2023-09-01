from py4web import action, request, abort, response, redirect, URL
from yatl.helpers import A
from py4web.utils.factories import ActionFactory, Inject

from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash, logger
import sys, os, random, json, uuid, string, secrets

from .left_menu import l_menu

from .ctrlpost import *
from .dbadm import *
from .sadm import *

from .ahelp import log_info, log_warn, log_debug
from .settings import APP_NAME


log_info('1'* 30)
log_warn('2'* 30)

@action("index")
@action.uses("index.html", auth, T, )
def index():
    # curl -k -I  https://192.168.1.161:9000/mig1ssl/index
    user = auth.get_user()

    log_warn('7'* 30 + ' ' +APP_NAME)
    log_info('9'* 30 + ' ' +APP_NAME)

    sio_users = ['userAAA', 'userBBB', 'userCCC', 'userDDD' ]
    #sio_users = ['userWWW','userXXX', 'userYYY', 'userZZZ', ]
    unm = secrets.choice(sio_users)
    message = T("Hello {first_name}".format(**user) if user else "Hello")
    actions = {"allowed_actions": auth.param.allowed_actions}
    response.headers["X-Username"] = unm 
    return dict(message=message, actions=actions, unm= unm, l_menu=l_menu)

