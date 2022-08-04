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


# https://blog.miguelgrinberg.com/post/beautiful-flask-tables-part-2


# ------------------------------------------------------------------------------


@action( "t1/basic_table",)
@action.uses( "basic_table.html", db, session, T,)
def basic_table():
    tbl = "user_table"
    return dict(users=db(db.user_table).select())


# ------------------------------------------------------------------------------


@action( "t1/ajax_table",)
@action.uses( "ajax_table.html", db, session, T,)
def ajax_table():
    return dict(data_url=URL("api_ajax/data"))


@action("api_ajax/data")
def api_ajax_data():
    tbl = "user_table"
    response.headers["Content-Type"] = "application/json"
    return json.dumps({"data": [user.as_dict() for user in db(db.user_table).select()]})


# ------------------------------------------------------------------------------


@action( "t1/server_table",)
@action.uses( "server_table.html", db, session, T,)
def server_table():
    return dict(data_url=URL("api_server/data"))


@action("api_server/data")
def api_server():
    tbl = "user_table"

    # field_objects = [f for f in db.user_table]
    # [db.user_table[fieldname] for fieldname in db.user_table.fields]

    users = []
    orderby_dict = {
        "name": db.user_table.name,
        "age": db.user_table.age,
        "email": db.user_table.email,
    }
    orderby = orderby_dict["name"]
    query = db.user_table

    # search filter
    search = request.GET.get("search")
    if search:
        query = db.user_table.name.contains(search,) | db.user_table.email.contains(
            search,
        )

    # sorting
    sort = request.GET.get("sort")
    if sort:
        order = []
        for s in sort.split(","):
            direction = s[0]
            name = s[1:]
            if name not in ["name", "age", "email"]:
                name = "name"
            orderby = ~orderby_dict[name] if direction == "-" else orderby_dict[name]

    # pagination
    start = int(request.GET.get("start", default=-1))
    length = int(request.GET.get("length", default=-1))
    if start != -1 and length != -1:
        users = db(query).select(limitby=(start, start + length), orderby=orderby)
    else:
        users = db(query).select(orderby=orderby)

    # response
    total = db(query).count()
    # print (users)
    response.headers["Content-Type"] = "application/json"
    return json.dumps(
        {
            "data": [user.as_dict() for user in users],
            "total": total,
        }
    )


# ------------------------------------------------------------------------------


@action( "t1/editable_table",)
@action.uses( "editable_table.html", db, session, T,)
def editable_table():
    return dict(data_url=URL("api_editable/data"))


@action("api_editable/data")
def api_editable():

    tbl = "user_table"

    users = []
    orderby_dict = {
        "name": db.user_table.name,
        "age": db.user_table.age,
        "email": db.user_table.email,
    }
    orderby = orderby_dict["name"]
    query = db.user_table

    # search filter
    search = request.GET.get("search")
    if search:
        query = db.user_table.name.contains(search,) | db.user_table.email.contains(
            search,
        )

    # sorting
    sort = request.GET.get("sort")
    if sort:
        order = []
        for s in sort.split(","):
            direction = s[0]
            name = s[1:]
            if name not in ["name", "age", "email"]:
                name = "name"

            orderby = ~orderby_dict[name] if direction == "-" else orderby_dict[name]

    # pagination
    start = int(request.GET.get("start", default=-1))
    length = int(request.GET.get("length", default=-1))

    if all([start != -1, length != -1]):
        users = db(query).select(limitby=(start, start + length), orderby=orderby)
    else:
        users = db(query).select(orderby=orderby)

    # response
    total = db(query).count()
    response.headers["Content-Type"] = "application/json"
    return json.dumps(
        {
            "data": [user.as_dict() for user in users],
            "total": total,
        }
    )


@action("api_editable/data", method=["POST"])
def editable_update():

    tbl = "user_table"

    try:
        u_data = json.loads(request.body.read())
    except Exception as ex:
        ex_template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        ex_msg = ex_template.format(type(ex).__name__, ex.args)
        print (ex_msg)
        return "bad"

    u_id = u_data.pop("id", None)

    if u_id is None:
        return f" u_id is None - {tbl},  abort(400)"

    user = db[tbl][u_id]
    #print(user)
    ret = db(db[tbl].id == u_id).validate_and_update(**u_data)
    if ret.get("updated", None) == 1:
        db.commit()

    #print(ret)
    #print(db[tbl][u_id])

    response.status = 204
