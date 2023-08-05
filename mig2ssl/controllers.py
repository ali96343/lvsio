from py4web import action, request, abort, response, redirect, URL
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash, logger
import sys, os, random, json, uuid, string, secrets

from .left_menu import l_menu

from .ctrlpost import *
from .dbadm import *
from .sadm import *

import logging


srv_log=None
def get_srv_logger(pat="PY4WEB:"):
    global srv_log
    if srv_log is None:
        h= [e for e in logging.root.manager.loggerDict
            if e.startswith(pat) ]
        srv_log = logging.getLogger(h[0])
        return srv_log
    return srv_log

@action("index")
@action.uses("index.html", auth, T)
def index():
    # curl -k -I  https://192.168.1.161:9000/mig1ssl/index
    user = auth.get_user()

    s_log = get_srv_logger()

    s_log.warn('00000000000000000000000000000000000000000000000000000')
    s_log.info('11111111111111111111111111111111111111111111111111111')

    #sio_users = ['userAAA', 'userBBB', 'userCCC', 'userDDD' ]
    sio_users = ['userWWW','userXXX', 'userYYY', 'userZZZ', ]
    unm = secrets.choice(sio_users)
    message = T("Hello {first_name}".format(**user) if user else "Hello")
    actions = {"allowed_actions": auth.param.allowed_actions}
    response.headers["X-Username"] = unm 
    return dict(message=message, actions=actions, unm= unm, l_menu=l_menu)

