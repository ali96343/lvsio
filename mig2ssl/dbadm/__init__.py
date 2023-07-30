from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
#from ..common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.factories import Inject
from pydal.tools.tags import Tags


from ..left_menu import l_menu

@action("mi1")
def mi1():
    return "its mi1" 


@action("mi2")
def mi2():
    return "its mi2" 

@action("mi3")
def mi3():
    return "its mi3" 

#@action("mi4")
#@action.uses("mi4.html", auth, T)
#def mi4():
#    user = auth.get_user()
#    message = T("mi4 Hello {first_name}".format(**user) if user else "mi4 Hello")
#    actions = {"allowed_actions": auth.param.allowed_actions}
#    return dict(message=message, actions=actions, l_menu=l_menu)
#
#
#@action("mi5")
#@action.uses("mi5.html", auth, T, Inject(l_menu=l_menu))
#def mi5():
#    user = auth.get_user()
#    message = T("mi5 Hello {first_name}".format(**user) if user else "mi5 Hello")
#    actions = {"allowed_actions": auth.param.allowed_actions}
#    return dict(message=message, actions=actions, )
