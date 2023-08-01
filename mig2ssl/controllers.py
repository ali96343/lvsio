from py4web import action, request, abort, response, redirect, URL
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
import sys, os, random, json, uuid, string, secrets

from .left_menu import l_menu

from .ctrlpost import *
from .dbadm import *
from .sioadm import *

@action("index")
@action.uses("index.html", auth, T)
def index():
    # curl -k -I  https://192.168.1.161:9000/mig1ssl/index
    user = auth.get_user()
    #sio_users = ['userAAA', 'userBBB', 'userCCC', 'userDDD' ]
    sio_users = ['userWWW','userXXX', 'userYYY', 'userZZZ', ]
    unm = secrets.choice(sio_users)
    message = T("Hello {first_name}".format(**user) if user else "Hello")
    actions = {"allowed_actions": auth.param.allowed_actions}
    response.headers["X-Username"] = unm 
    return dict(message=message, actions=actions, unm= unm, l_menu=l_menu)

