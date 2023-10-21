"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""

from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash


import sys
import logging
from .common import logger
from .settings import APP_NAME
from threading import Lock


_srv_log=None

def log_info(mess, dbg=True, ):
    def salog(pat='SA:'):
        global _srv_log
        if _srv_log: # and isinstance( __srv_log, logging.Logger ):
           return _srv_log

        hs= [e for e in logging.root.manager.loggerDict if e.startswith(pat) ]
        if len(hs) == 0:
            return logger

        sa_lock = Lock()
        with sa_lock:
            _srv_log = logging.getLogger(hs[0])

        return _srv_log

    caller = f" > {APP_NAME} > {sys._getframe().f_back.f_code.co_name}"
    dbg and salog().info(mess + caller)


log_warn=log_info
log_debug=log_info

log_warn('0'* 30 )


@action("index")
@action.uses("index.html", auth, T)
def index():



    log_warn('7'* 30 )
    log_info('9'* 30 )

    user = auth.get_user()
    message = T("Hello {first_name}").format(**user) if user else T("Hello")
    actions = {"allowed_actions": auth.param.allowed_actions}
    return dict(message=message, actions=actions)
