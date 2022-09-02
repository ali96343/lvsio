from py4web import action, request, response, abort, redirect, URL, Field
from py4web.utils.cors import CORS
from py4web.utils.form import Form, FormStyleDefault
from pydal.validators import IS_NOT_EMPTY
from yatl.helpers import A, DIV
from ..common import (
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
import logging, os, sys

from time import sleep
from datetime import datetime
from random import randint
import redis
import json
from functools import reduce

from ..models import grps, x_groups, x_permissions


@action("adm1/find_tag/{group_name}")
@action.uses(db)
def find_tag(group_name):
    users = db(grps.find([group_name])).select(
        orderby=db.auth_user.first_name | db.auth_user.last_name
    )
    return {"users": users}


# ----------------------------------------------------------------
@action("adm1/zap")
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


