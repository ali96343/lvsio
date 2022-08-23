from py4web import action, request, response, abort, redirect, URL, Field
from py4web.utils.cors import CORS
from py4web.utils.form import Form, FormStyleDefault
from pydal.validators import IS_NOT_EMPTY
from yatl.helpers import A, DIV, XML, SELECT, OPTION
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


# https://stackoverflow.com/questions/67166839/how-to-show-a-table-with-tabulator-using-flask-and-a-json-variable 
# https://webdevkin.ru/posts/frontend/tabulator
# https://webdevkin.ru/examples/tabulator/
# https://javascript.tutorialink.com/tabulator-processing-ajax-data-before-load/
# https://www.tmssoftware.com/site/blog.asp?post=948
# https://coldfusion.adobe.com/2019/11/using-coldfusion-tabulator-wordpress-unison/



# ------------------------------------------------------------------------------

@action( "t1/basic_table",)
@action.uses( "t1/basic_table.html", db, session, T,)
def t1_basic_table():
    tbl = "user_table"
    query = db[tbl]
    data = [u.as_dict() for u in db(query).select()]
    return dict(data=data)

# ------------------------------------------------------------------------------
#
@action( "t1/ajax_table",)
@action.uses( "t1/ajax_table.html", db, session, T,)
def t1_ajax_table():
    return dict(data_url=URL("t1/api_ajax/data"))
#
#
@action("t1/api_ajax/data")
def t1_api_ajax_data():
    tbl = "user_table"
    query = db[tbl]
    response.headers["Content-Type"] = "application/json"
    return json.dumps([u.as_dict() for u in db(query).select()])


# ------------------------------------------------------------------------------
#
@action( "t1/server_table",)
@action.uses( "t1/server_table.html", db, session, T,)
def t1_server_table():
    tbl = "user_table"
    all_fields =  [f for f in db[tbl].fields ]

    columns = [ (f, db[tbl][f].label) for f in all_fields]
    #columns.insert(0, ( '', '') )
    opts = [OPTION(k, _value=k) for k,v in columns]
    #opts = [OPTION(k, _value=v) for k,v in columns]
    attr = dict( _id = "filter-field" )

    oper = [ ('like','like'), ('=','='), ('<','<'), ('<=','<='), ('>','>'), ('>=','>=' ), ('!=','!='), ]
    opts_oper = [OPTION(k, _value=v) for k,v in oper]
    attr_oper = dict( _id = "filter-type" )

    return dict(data_url=URL("t1/api_server/data"), 
                sel=SELECT(*opts, **attr ), 
                sel_oper = SELECT(*opts_oper, **attr_oper ),
           )
#
#
@action("t1/api_server/data")
def t1_api_server_data():
    tbl = "user_table"
    query = db[tbl]
    orderby = db[tbl].id 

# http://tabulator.info/docs/5.3/data#ajax-filter

    print ('---------------------')
    rdict =  dict(request.query)  
    for k,v in  rdict.items(): 
        print (k,'  ',v)

    # search

    #filter[0][field]    address
    #filter[0][type]    =
    #filter[0][value]    cccc

    if 'filter[0][field]' in rdict:
        fld = rdict['filter[0][field]']
        val = rdict['filter[0][value]']
        oper = rdict['filter[0][type]']
        print (oper)
        if oper in [ '=', '<', '<=', '>', '>=', '!=', ]:
             if oper == '=':
                oper = '=='
             query = eval ( 'db[tbl][fld]' + oper +  'val' )
        elif oper in [ 'like', ]:
             if db[tbl][fld].type == 'string':
                 print ('ok')
                 query = db[tbl][fld].contains( val ) 
                
    # sort
    if 'sort[0][field]' in rdict:
        fld = rdict['sort[0][field]']
        direction = rdict['sort[0][dir]']
        orderby = db[tbl][fld]
        if direction == 'asc':
           orderby = ~orderby


    #from urllib.parse import parse_qs

    #d = parse_qs(request.query_string)
    #print('d= ',d)


    response.headers["Content-Type"] = "application/json"
    return json.dumps([u.as_dict() for u in db(query).select(orderby = orderby)])


