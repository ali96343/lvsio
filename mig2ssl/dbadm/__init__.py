from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
#from ..common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.factories import Inject
from pydal.tools.tags import Tags


from .atab_utils import sql2table 
from .tlist_utils import *


from ..left_menu import l_menu

@action("mi1_db")
def mi1_db():
    return "its mi1_db" 


@action("mi2_db")
def mi2_db():
    return "its mi2_db" 

@action("mi3_db")
def mi3_db():
    return "its mi3_db" 

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
