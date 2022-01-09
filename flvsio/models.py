"""
This file defines the database models
"""

import os, sys
from .common import db, Field
from pydal.validators import *

### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later
#
# db.commit()
#


class Mk_table:
    def __init__(
        self,
        tbl_name="my_tbl",
        fld_types=["integer", "integer"],
        init_value=[100, 100],
        init_array=[],
    ):
        self.tbl_name = tbl_name
        self.fld_types = fld_types
        self.init_value = init_value
        self.f_names = [f"f{i}" for i, e in enumerate(self.fld_types)]
        self.init_array = init_array

    def ins_row(self,):
        if self.init_value:
            c = {f"f{i}": e for i, e in enumerate(self.init_value)}
            db[self.tbl_name].insert(**db[self.tbl_name]._filter_fields(c))
            db.commit()

    def ins_array(self,):
        if self.init_array:
            for e in self.init_array:
                c = dict()
                c[self.f_names[0]] = e
                db[self.tbl_name].insert(**db[self.tbl_name]._filter_fields(c))
            db.commit()

    def create(self,):
        fs = [ Field(f"f{i}", f"{e}", label=f"l{i}") for i, e in enumerate(self.fld_types) ]
        db.define_table(self.tbl_name, tuple(fs) )
        db.commit()

    @property
    def do(self,):
        self.create()
        if not db(db[self.tbl_name]).count():
                self.ins_row()
                self.ins_array()
        return [e for e in db.tables]


Mk_table(tbl_name="Longtask", fld_types=["string",], init_value=['hello']).do
Mk_table(tbl_name="ImaSize", fld_types=["integer",], init_value=[100]).do
Mk_table(tbl_name="Counter", fld_types=["integer",], init_value=[0]).do
Mk_table( tbl_name="Sliders", fld_types=["integer", "integer", "string"], init_value=[100, 100, "hi!"],).do

from .mcountries import countries

Mk_table( tbl_name="Autocomplete", fld_types=["string"], init_value=[], init_array=countries).do
