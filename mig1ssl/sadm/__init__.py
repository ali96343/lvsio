from py4web import action, request, abort, redirect, URL
from yatl.helpers import A, I, SPAN, XML, DIV, P
from py4web import action, request, response, abort, redirect, URL, Field
from ..common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.form import Form, FormStyleBulma
import copy

from ..left_menu import l_menu



@action("spa-7531", method=["GET", "POST"])
@action.uses(db, session, T, "spa-7531.html")
def spa_7531():
    return dict(l_menu=l_menu)

@action("spa-67", method=["GET", "POST"])
@action.uses(db, session, T, "spa-67.html")
def spa_67():
    return dict(l_menu=l_menu)

@action("spa-55", method=["GET", "POST"])
@action.uses(db, session, T, "spa-55.html")
def spa_55():
    return dict(l_menu=l_menu)

@action("spa-45", method=["GET", "POST"])
@action.uses(db, session, T, "spa-45.html")
def spa_45():
    return dict(l_menu=l_menu)

@action("spa-364", method=["GET", "POST"])
@action.uses(db, session, T, "spa-364.html")
def spa_364():
    return dict(l_menu=l_menu)

@action("spa-324", method=["GET", "POST"])
@action.uses(db, session, T, "spa-324.html")
def spa_324():
    return dict(l_menu=l_menu)

@action("spa-300", method=["GET", "POST"])
@action.uses(db, session, T, "spa-300.html")
def spa_300():
    return dict(l_menu=l_menu)
