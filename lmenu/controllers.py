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


from .left_menu import l_menu


@action("index")
@action.uses("index.html", auth, T)
def index():
    user = auth.get_user()
    message = T("index Hello {first_name}".format(**user) if user else "index Hello")
    actions = {"allowed_actions": auth.param.allowed_actions}
    return dict(message=message, actions=actions, l_menu=l_menu)



@action("mi1")
def mi1():
    return "its mi1" 


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
    message = T("imi4 Hello {first_name}".format(**user) if user else "mi4 Hello")
    actions = {"allowed_actions": auth.param.allowed_actions}
    return dict(message=message, actions=actions, l_menu=l_menu)


@action("mi5")
@action.uses("mi5.html", auth, T)
def mi5():
    user = auth.get_user()
    message = T("imi5 Hello {first_name}".format(**user) if user else "mi5 Hello")
    actions = {"allowed_actions": auth.param.allowed_actions}
    return dict(message=message, actions=actions, )


