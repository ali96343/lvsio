from py4web import action, request, abort, redirect, URL
from yatl.helpers import A, I, SPAN, XML, DIV, P
from py4web import action, request, response, abort, redirect, URL, Field
from ..common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.form import Form, FormStyleBulma
import copy

from ..left_menu import l_menu


@action("js_count", method=["GET", "POST"])
@action.uses(db, session, T, "js-count.html")
def js_count():
    return dict(l_menu=l_menu)


