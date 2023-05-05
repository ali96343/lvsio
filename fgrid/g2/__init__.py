from py4web import action, request, response, abort, redirect, URL, Field
from py4web.utils.cors import CORS
from py4web.utils.form import Form, FormStyleDefault
from pydal.validators import IS_NOT_EMPTY
from yatl.helpers import A, DIV
from py4web.utils.url_signer import URLSigner
from py4web.utils.factories import Inject
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


url_signer = URLSigner(session, signing_info=lambda: str("user=xxxxxxxxxxxx")) 
url_signer_no_session = URLSigner(signing_info=lambda: str("user=yyyyyyyyyyyyyy")) 


# https://blog.miguelgrinberg.com/post/beautiful-flask-tables-part-2

# ------------------------------------------------------------------------------

@action( "g2/basic_table",)
@action.uses( "g2/basic_table.html", db, session, T,)
@action.uses( url_signer_no_session.verify(), )
def g2_basic_table():

    #headers_string = ['{}: {}'.format(h, request.headers.get(h)) for h in request.headers.keys()] 
    #print('URL={}, method={}\nheaders:\n{}'.format(request.url, request.method, '\n'.join(headers_string)))

    print ( "signed_url_no_session:" + request.url )
    my_url = request.url

    tbl = "user_table"

    fields =  [f for f in db[tbl].fields ]
    columns = [ {'id':f, 'name': db[tbl][f].label} for f in fields]
    ftypes = [ {f : db[tbl][f].type} for f in fields if  db[tbl][f].type == 'string']
    query = db[tbl]
    data = [ u.as_dict() for u in db(query).select() ]
    return dict(data=data,  columns= columns, my_url=my_url )

# ------------------------------------------------------------------------------

@action( "g2/ajax_table",)
@action.uses( "g2/ajax_table.html", db, session, T, url_signer)
def g2_ajax_table():
    tbl = "user_table"
    columns = [ {'id':f, 'name': db[tbl][f].label} for f in db[tbl].fields]
    return dict(data_url=URL("g2/api_ajax/data", signer = url_signer), columns=columns,)


@action("g2/api_ajax/data")
@action.uses(url_signer, session, url_signer.verify())
def g2_api_ajax_data():
    tbl = "user_table"
    query = db[tbl]
    response.headers["Content-Type"] = "application/json"
    return json.dumps({"data": [u.as_dict() for u in db(query).select()], })

# ------------------------------------------------------------------------------


@action( "g2/server_table",)
@action.uses( "g2/server_table.html", db, session, T, url_signer)
def g2_server_table():
    tbl = "user_table"
    columns = [ {'id':f, 'name': db[tbl][f].label} for f in db[tbl].fields]
    columnIds = [ f for f in db[tbl].fields ]
    return dict(data_url=URL("g2/api_server/data", signer = url_signer ), columns=columns, columnIds=columnIds )


@action("g2/api_server/data")
@action.uses(session, url_signer, url_signer.verify(), )
def g2_api_server():

    tbl = "user_table"

    all_fields =  [f for f in db[tbl].fields ]
    columns = [ {'id':f, 'name': db[tbl][f].label} for f in all_fields]
    sfields = [ f  for f in all_fields if  db[tbl][f].type == 'string']
    fields = sfields #['name','address','email','phone']
    orderby = db[tbl].fields[0]

    query = db[tbl]
    columnIds = [ f for f in db[tbl].fields ]

    # search filter
    search = request.GET.get("search")
    if search:
        #fields = ['name','address','email', 'phone']
        qt = [db.user_table[f].contains(search) for f in fields]
        query = reduce( lambda a,b: a| b, qt  )

    # sorting
    sort = request.GET.get("sort")
    if sort:
        order = []
        for s in sort:
          if s:
            direction, name = s[0], s[1:]
            if name not in fields: # ["name", "age", "email", ]:
                name = fields[0] #"name"

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


@action( "g2/editable_table",)
@action.uses( "g2/editable_table.html", db, session, T, url_signer)
def g2_editable_table():
    tbl = "user_table"
    columns = [ {'id':f, 'name': db[tbl][f].label} for f in db[tbl].fields]
    columnIds = [ f for f in db[tbl].fields ]
    return dict(data_url=URL("g2/api_editable/data", signer=url_signer), columns=columns, columnIds=columnIds)


@action("g2/api_editable/data")
@action.uses( session, url_signer, url_signer.verify(), )
def g2_api_editable():

    tbl = "user_table"

    query = db[tbl]

    all_fields =  [f for f in db[tbl].fields ]
    columns = [ {'id':f, 'name': db[tbl][f].label} for f in all_fields]
    sfields = [ f  for f in all_fields if  db[tbl][f].type == 'string']
    fields = sfields #['name','address','email','phone']
    orderby = db[tbl].fields[0]



    # search filter
    search = request.GET.get("search")
    if search:
        qt = [db[tbl][f].contains(search) for f in fields]
        query = reduce( lambda a,b: a| b, qt  )

    # sorting
    sort = request.GET.get("sort")
    if sort:
        order = []
        for s in sort:
          if s:
            direction, name = s[0], s[1:]

            #if name not in ["name", "age", "email", ]:
            if name not in fields:
                name = fields[0] #"name"

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


@action("g2/api_editable/data", method=["POST"])
@action.uses( session, url_signer, url_signer.verify(), )
def g2_editable_update():

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
