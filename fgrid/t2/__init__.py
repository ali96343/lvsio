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


from py4web.utils.url_signer import URLSigner
url_signer = URLSigner(session, lifespan=3600, signing_info=lambda: str("user=xxxxxxxxxxxx")   )
url_t2_signer = URLSigner(lifespan=3600,  signing_info=lambda: str("user=yyyyyyyyyyyyyy")  )

# https://dev.to/rfornal/-replacing-jquery-with-vanilla-javascript-1k2g
# https://tobiasahlin.com/blog/move-from-jquery-to-vanilla-javascript/


# https://stackoverflow.com/questions/67166839/how-to-show-a-table-with-tabulator-using-flask-and-a-json-variable 
# https://webdevkin.ru/posts/frontend/tabulator
# https://webdevkin.ru/examples/tabulator/
# https://javascript.tutorialink.com/tabulator-processing-ajax-data-before-load/
# https://www.tmssoftware.com/site/blog.asp?post=948
# https://coldfusion.adobe.com/2019/11/using-coldfusion-tabulator-wordpress-unison/
# https://www.c-sharpcorner.com/article/display-data-in-tabulator-js-table-from-c-sharp/
# https://www.enjoysharepoint.com/tabulator-js-tutorial/
# https://kvision.gitbook.io/kvision-guide/v/kvision-1.x/part-2-advanced-features/tabulator-tables

# https://habr.com/ru/post/448072/
# https://habr.com/ru/post/256045/


# ------------------------------------------------------------------------------
# https://github.com/dreamfactorysoftware/dreamfactory-tabulator/blob/master/index.html

# title: This will be table column display name
# field: Data source field from the data source
# sorter: If you are trying to sort text field, then we have to mention string. 
#   Similarly, for the integer type field write “number“, and for DateTime type, we have to write “date“.
# headerFilter: “input”: If you want to have a filter option below to the header, 


# https://github.com/dreamfactorysoftware/dreamfactory-tabulator/blob/master/index.html
@action( "t2/basic_table_ex2",)
@action.uses( "t2/basic_table_ex2.html", db, session, T,)
def t2_basic_table_ex2():
    return dict()

@action( "t2/basic_table_ex1",)
@action.uses( "t2/basic_table_ex1.html", db, session, T,)
def t2_basic_table_ex1():
    return dict()

@action( "t2/basic_table_ex3",)
@action.uses( "t2/basic_table_ex3.html", db, session, T,)
def t2_basic_table_ex3():
    return dict()

@action( "t2/basic_table",)
@action.uses( "t2/basic_table.html", db, session, T,)
def t2_basic_table():
    tbl = "user_table"
    query = db[tbl]

    all_fields =  [f for f in db[tbl].fields ]
    col = [ (f, db[tbl][f].label, db[tbl][f].type) for f in all_fields]
    #col.append(columns.pop(0))
    print (col)

    columns = []
    for f, l, t in col:
       print (f)
       tmp = dict()
       tmp['title'] = l
       tmp['field'] = f
       if t in ['id', 'integer']:
           t = 'number'
       if t in ['datetime']:
           t = 'date' 
       tmp['sorter'] = t 
       tmp['headerFilter'] = 'input' 
       tmp['hozAlign'] = 'left' 
       columns.append( tmp )

    print (columns)

    data = [u.as_dict() for u in db(query).select()]
    return dict(data=data, columns=columns)

#
#
## ------------------------------------------------------------------------------
##
#@action( "t2/ajax_table",)
#@action.uses( "t2/ajax_table.html", db, session, T, url_signer)
#def t2_ajax_table():
#    return dict(data_url=URL("t2/api_ajax/data", signer= url_signer))
##
##
#@action("t2/api_ajax/data")
#@action.uses(url_signer.verify())
#def t2_api_ajax_data():
#    tbl = "user_table"
#    query = db[tbl]
#    response.headers["Content-Type"] = "application/json"
#    return json.dumps([u.as_dict() for u in db(query).select()])
#
#
## ------------------------------------------------------------------------------
##
#@action( "t2/server_table",)
#@action.uses( "t2/server_table.html", db,url_signer, session, T,)
#def t2_server_table():
#    tbl = "user_table"
#    all_fields =  [f for f in db[tbl].fields ]
#
#    columns = [ (f, db[tbl][f].label) for f in all_fields]
#    columns.append(columns.pop(0))
#    #columns.insert(0, ( '', '') )
#    opts = [OPTION(k, _value=k) for k,v in columns]
#    #opts = [OPTION(k, _value=v) for k,v in columns]
#    attr = dict( _id = "filter-field" )
#
#    oper = [ ('like','like'), ('=','='), ('<','<'), ('<=','<='), ('>','>'), ('>=','>=' ), ('!=','!='), ]
#    opts_oper = [OPTION(k, _value=v) for k,v in oper]
#    attr_oper = dict( _id = "filter-type" )
#
#    return dict(data_url=URL("t2/api_server/data", signer=url_signer), 
#                sel=SELECT(*opts, **attr ), 
#                sel_oper = SELECT(*opts_oper, **attr_oper ),
#           )
##
##
#@action("t2/api_server/data")
#@action.uses(url_signer.verify())
#def t2_api_server_data():
#
#    tbl = "user_table"
#    query = db[tbl]
#    orderby = db[tbl].id 
#
## http://tabulator.info/docs/5.3/data#ajax-filter
#
#    print ('---------------------')
#    rdict =  dict(request.query)  
#    for k,v in  rdict.items(): 
#        print (k,'  ',v)
#
#    # search
#
#    #filter[0][field]    address
#    #filter[0][type]    =
#    #filter[0][value]    cccc
#
#    if 'filter[0][field]' in rdict:
#        fld = rdict['filter[0][field]']
#        val = rdict['filter[0][value]']
#        oper = rdict['filter[0][type]']
#        print (oper)
#        if oper in [ '=', '<', '<=', '>', '>=', '!=', ]:
#             if oper == '=':
#                query = db[tbl][fld] == val 
#             elif oper == '>':
#                query = db[tbl][fld] > val 
#             elif oper == '>=':
#                query = db[tbl][fld] >= val 
#             elif oper == '<':
#                query = db[tbl][fld] < val 
#             elif oper == '<=':
#                query = db[tbl][fld] <= val 
#             elif oper == '!=':
#                query = db[tbl][fld] != val 
#
#             #query = eval ( 'db[tbl][fld]' + oper +  'val' )
#
#        elif oper in [ 'like', ]:
#             if db[tbl][fld].type == 'string':
#                 #print ('ok')
#                 query = db[tbl][fld].contains( val ) 
#    # sort
#    if 'sort[0][field]' in rdict:
#        fld = rdict['sort[0][field]']
#        direction = rdict['sort[0][dir]']
#        orderby = db[tbl][fld]
#        if direction == 'asc':
#           orderby = ~orderby
#
#
#    #from urllib.parse import parse_qs
#
#    #d = parse_qs(request.query_string)
#    #print('d= ',d)
#
#
#    response.headers["Content-Type"] = "application/json"
#    return json.dumps([u.as_dict() for u in db(query).select(orderby = orderby)])
#
#
