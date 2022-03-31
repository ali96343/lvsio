"""
This file defines the database models
"""

import os, sys
from .common import db, Field
from pydal.validators import *

from pydal.tools.tags import Tags
from py4web.utils.populate import populate
import datetime


### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later
#
# db.commit()
#

if not db(db.auth_user).count():
    u1 = {
        "username": "anil",
        "email": "anil@nil.com",
        "password": str(CRYPT()("xyz12345")[0]),
        "first_name": "Anil_first",
        "last_name": "Anil_Last",
    }

    u2 = {
        "username": "bnil",
        "email": "bnil@nil.com",
        "password": str(CRYPT()("xyz12345")[0]),
        "first_name": "Bnil_first",
        "last_name": "Bnil_Last",
    }

    u3 = {
        "username": "cnil",
        "email": "cnil@nil.com",
        "password": str(CRYPT()("xyz12345")[0]),
        "first_name": "Cnil_first",
        "last_name": "Cnil_Last",
    }

    for e in [u1, u2, u3]:
        db.auth_user.insert(**db.auth_user._filter_fields(e))
    db.commit()

    groups = Tags(db.auth_user)

    groups.add(1, "manager")
    groups.add(2, ["dancer", "teacher"])
    groups.add(3, "dancer")
    db.commit()

"""
signature = db.Table(
    db,
    "signature",
    Field("is_active", "boolean", default=True),
    Field("created_on", "datetime", default= datetime.datetime.now() ),
    Field("created_by", db.auth_user, default=auth.user_id),
    Field("modified_on", "datetime", update= datetime.datetime.now()),
    Field("modified_by", db.auth_user, update=auth.user_id),
)
"""



db.define_table(
    "uploaded_files",
    Field("orig_file_name", requires=IS_NOT_EMPTY(),),
    Field("remark", "text",),
    Field("uniq_file_name", requires=IS_NOT_EMPTY(),),
    Field( "time", "datetime", editable=False, default=datetime.datetime.now(), requires=IS_DATETIME(),),
)

db.commit()

class Mk_table:

    # my_pep: Z === self

    def __init__(
        Z,
        tbl_name="my_tbl",
        fld_types=[],  # ["integer", "integer"],
        init_value=[],  # [100, 100],
        init_array=[],
        init_populate=0,
    ):
        Z.tbl_name = tbl_name
        Z.fld_types = fld_types
        Z.init_value = init_value
        Z.f_names = [f"f{i}" for i, e in enumerate(Z.fld_types)]
        Z.init_array = init_array
        Z.init_populate = init_populate

    def ins_row(Z,):
        if Z.init_value:
            v = {f"f{i}": e for i, e in enumerate(Z.init_value)}
            db[Z.tbl_name].insert(**db[Z.tbl_name]._filter_fields(v))
            db.commit()

    def ins_populate(Z,):
        if Z.init_populate > 0:
            populate(db[Z.tbl_name], n=Z.init_populate)
            db.commit()

    def ins_array(Z,):
        if Z.init_array:
            for e in Z.init_array:
                c = dict()
                c[Z.f_names[0]] = e
                db[Z.tbl_name].insert(**db[Z.tbl_name]._filter_fields(c))
            db.commit()

    @property
    def do(Z,):
        if Z.fld_types:
            fs = [ Field(f"f{i}", f"{e}", label=f"l{i}") for i, e in enumerate(Z.fld_types) ] 
            db.define_table(Z.tbl_name, tuple(fs))
            db.commit()

            if not db(db[Z.tbl_name]).count():
                Z.ins_row()
                Z.ins_array()
                Z.ins_populate()
        # return [e for e in db.tables]


#Mk_table( tbl_name="test_table", fld_types=["string", "string", "string"], init_populate=50).do
#Mk_table( tbl_name="Longtask",   fld_types=["string",], init_value=["hello"]).do
Mk_table( tbl_name="sse_tmp_value",    fld_types=["integer",], init_value=[99999999999]).do
#Mk_table( tbl_name="Counter",    fld_types=["integer",], init_value=[0]).do
#Mk_table( tbl_name="Sliders",    fld_types=["integer", "integer", "string"], init_value=[100, 100, "hi!"],).do

