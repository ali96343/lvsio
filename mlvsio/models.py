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


def mk_table(
    tbl_name="my_tbl", fld_list=["integer", "integer"], init_value=[7, 7], ins_array=[]
):

    fs = tuple([Field(f"f{i}", f"{e}", label=f"l{i}") for i, e in enumerate(fld_list)])
    db.define_table(tbl_name, fs)
    db.commit()

    f_names = [f"f{i}" for i, e in enumerate(fld_list)]
    if (not db(db[tbl_name]).count()) and len(init_value):
        c = {f"f{i}": e for i, e in enumerate(init_value)}
        db[tbl_name].insert(**db[tbl_name]._filter_fields(c))
        db.commit()

    elif (not db(db[tbl_name]).count()) and (len(init_value) == 0) and ins_array:
        if (not isinstance(ins_array[0], (list, tuple))) and len(f_names) == 1:
            c = dict()
            for e in ins_array:
                c[f_names[0]] = e
                db[tbl_name].insert(**db[tbl_name]._filter_fields(c))
            db.commit()
        else:
            sys.exit("unk if in models.mk_table")

    return [e for e in db.tables]


mk_table(tbl_name="ImaSize", fld_list=["integer",], init_value=[100])
mk_table(tbl_name="Counter", fld_list=["integer",], init_value=[0])
mk_table(tbl_name="Sliders", fld_list=["integer", "integer", "string"], init_value=[100, 100, 'hi!'])

from .mcountries import countries
mk_table(tbl_name="Autocomplete", fld_list=["string"], init_value=[], ins_array=countries)
