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


# https://blog.miguelgrinberg.com/post/beautiful-flask-tables-part-2

# ------------------------------------------------------------------------------

@action( "g1/basic_table",)
@action.uses( "g1/basic_table.html", db, session, T,)
def g1_basic_table():
    tbl = "user_table"
    return dict(users=db(db.user_table).select())

# ------------------------------------------------------------------------------

@action( "g1/ajax_table",)
@action.uses( "g1/ajax_table.html", db, session, T,)
def g1_ajax_table():
    return dict(data_url=URL("g1/api_ajax/data"))


# curl http://localhost:8000/fgrid/g1/api_ajax/data -H "Accept: application/json"
@action("g1/api_ajax/data")
def g1_api_ajax_data():
    tbl = "user_table"
    #query = db.user_table
    query = db[tbl]
    response.headers["Content-Type"] = "application/json"
    return json.dumps({"data": [u.as_dict() for u in db(query).select()]})

# ------------------------------------------------------------------------------


@action( "g1/server_table",)
@action.uses( "g1/server_table.html", db, session, T,)
def g1_server_table():
    return dict(data_url=URL("g1/api_server/data"))


@action("g1/api_server/data")
def g1_api_server():

    tbl = "user_table"

    # field_objects = [f for f in db.user_table]
    # [db.user_table[fieldname] for fieldname in db.user_table.fields]

    users = []
    orderby = db.user_table.name 

    query = db.user_table

    # search filter
    search = request.GET.get("search")
    if search:
        fields = ['name','address','email', 'phone']
        qt = [db.user_table[f].contains(search) for f in fields]
        query = reduce( lambda a,b: a| b, qt  )

    # sorting
    sort = request.GET.get("sort")
    #if sort and (not any(e is True  for e in sort) ):
    if sort :
        order = []
        for s in sort:
          if s:
            direction, name = s[0], s[1:]
            if name not in ["name", "age", "email", ]:
                name = "name"

            orderby = db.user_table[name]
            if direction == "-":
                 orderby = ~orderby

    # pagination
    (start, length) = (
        int(request.GET.get("start", -1)),
        int(request.GET.get("length", -1)),
    )

    users = (
        db(query).select(limitby=(start, start + length), orderby=orderby)
        if all([start != -1, length != -1])
        else db(query).select(orderby=orderby)
    )

    # response
    response.headers["Content-Type"] = "application/json"
    return json.dumps(
        {
            "data": [u.as_dict() for u in users],
            "total": len(users), # db(query).count(), 
        }
    )


# ------------------------------------------------------------------------------


@action( "g1/editable_table",)
@action.uses( "g1/editable_table.html", db, session, T,)
def g1_editable_table():
    return dict(data_url=URL("g1/api_editable/data"))


@action("g1/api_editable/data")
def g1_api_editable():

    tbl = "user_table"

    users = []
    orderby = db.user_table.name 
    query = db.user_table

    # search filter
    search = request.GET.get("search")
    if search:
        fields = ['name','address','email','phone']
        qt = [db.user_table[f].contains(search) for f in fields]
        query = reduce( lambda a,b: a| b, qt  )

    # sorting
    sort = request.GET.get("sort")
    if sort:
        order = []
        for s in sort:
           if s:
              direction, name = s[0], s[1:]

              if name not in ["name", "age", "email", ]:
                  name = "name"

              orderby = db.user_table[name]
              if direction == "-":
                  orderby = ~orderby

    # pagination
    try:
        (start, length) = (
            int(request.GET.get("start")),
            int(request.GET.get("length")),
        )
    except ValueError:
       start, length = None, None

    users = (
        db(query).select(limitby=(start, start + length), orderby=orderby)
        if all([start , length ])
        else db(query).select(orderby=orderby)
    )

    # response
    response.headers["Content-Type"] = "application/json"
    return json.dumps(
        {
            "data": [u.as_dict() for u in users],
            "total": len(users), # db(query).count(), 
        }
    )


@action("g1/api_editable/data", method=["POST"])
def g1_editable_update():

    tbl = "user_table"
    if request.headers.get("Content-Type") != "application/json":
        return "bad Content-Type: editable_update"

    try:
        u_data = json.loads(request.body.read())
    except Exception as ex:
        ex_template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        ex_msg = ex_template.format(type(ex).__name__, ex.args)
        print (ex_msg)
        return "bad json: editable_update"

    u_id = u_data.pop("id", None)

    if u_id is None:
        return f"u_id is None - {tbl},  abort(400)"

    user = db[tbl][u_id]

    #print(user)
    ret = db(db[tbl].id == u_id).validate_and_update(**u_data)
    if ret.get("updated", None) == 1:
        db.commit()

    #print(ret)
    #print(db[tbl][u_id])

    response.status = 204
