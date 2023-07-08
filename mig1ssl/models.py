from .common import db, Field
from pydal.validators import *
from py4web.utils.populate import populate
from datetime import datetime
from pydal.tools.tags import Tags

#import pydal
#from py4web import *
#from apps.lmenu.models import db


# https://py4web.com/_documentation/static/en/chapter-13.html?highlight=tags

grps = Tags(db.auth_user, 'grps')
db.commit()

db.define_table('auth_group', Field('name'), Field('description'))
db.commit()

x_groups = Tags(db.auth_user,'x')
db.commit()
x_permissions = Tags(db.auth_group,'x')
db.commit()


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

    for e in [u1, u2, u3]: db.auth_user.insert(**db.auth_user._filter_fields(e) )
    db.commit()


    grps.add(1, 'manager')
    grps.add(2, ['dancer', 'teacher'])
    grps.add(3,'dancer')
    grps.add(3,'dancer')
    grps.add(3,'dancer')
    grps.add(3,'dancer')
    grps.add(3,'dancer')
    grps.add(3,'manager')
    db.commit()

    #print( db(db.auth_user_tag_grps).select() )


    zap_id = db.auth_group.insert(name='zapper', description='can zap database')
    x_permissions.add(zap_id, 'zap database')
    #x_groups.add(user.id, 'zapper')
    x_groups.add(1, 'zapper')
    db.commit()

db.define_table( 'uploaded_files',
    Field('orig_file_name', requires=IS_NOT_EMPTY(),  ),
    Field("remark",'text',),
    Field('uniq_file_name', requires=IS_NOT_EMPTY(),  ),
    Field('time', 'datetime', editable=False, default = datetime.now(), requires = IS_DATETIME( )),
    )

db.commit()

# --------------------------------------------------------------------------------
from random import randint
from faker import Faker

def GenUserItems(max=0):
    n = 0
    faker = Faker()
    while n < max:
        user = dict(name=faker.name(),
                   age=randint(20, 80),
                   address=faker.address().replace('\n', ', '),
                   phone=faker.phone_number(),
                   email=faker.email()
               )
        yield user
        n += 1

class Mk_table:

    # my_pep: Z === self

    def __init__(
        Z,
        tbl_name="my_tbl",
        fld_types=[],  # ["integer", "integer"],
        init_value=[],  # [100, 100],
        init_array=[],
        init_populate=0,
        init_faker=0,
        faker_generator=None
    ):
        Z.tbl_name = tbl_name
        Z.fld_types = fld_types
        Z.init_value = init_value
        Z.f_names = [f"f{i}" for i, e in enumerate(Z.fld_types)]
        Z.init_array = init_array
        Z.init_populate = init_populate
        Z.init_faker = init_faker
        Z.faker_generator=faker_generator

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

    def ins_faker(Z,):
        if Z.init_faker and Z.faker_generator:
            for c in Z.faker_generator(Z.init_faker):
                 #print( c )
                 db[Z.tbl_name].insert(**db[Z.tbl_name]._filter_fields(c))
            db.commit()

    def do(Z,):
        if Z.fld_types:
            if isinstance( Z.fld_types  , (list, tuple)):
                fs = [ Field(f"f{i}", f"{e}", label=f"l{i}") for i, e in enumerate(Z.fld_types) ] 
                db.define_table(Z.tbl_name, tuple(fs))
                db.commit()

                if not db(db[Z.tbl_name]).count():
                    Z.ins_row()
                    Z.ins_array()
                    Z.ins_populate()
            elif isinstance( Z.fld_types, (dict)):
                fs = [ Field(f"{k}", f"{v}",  label=f"l{k}" ) for k, v in Z.fld_types.items() ] 
                db.define_table(Z.tbl_name, tuple(fs))
                db.commit()
                if not db(db[Z.tbl_name]).count():
                    Z.ins_faker()
               
            else:    
               print ('not released! - models.py')
        # return [e for e in db.tables]


#Mk_table( tbl_name="xxx", fld_types=["string", "integer", "string", "string", 'string'], init_populate=50).do()

Mk_table( tbl_name="test_table", fld_types=["string", "string", "string", ], init_populate=50).do()

Mk_table( tbl_name="user_table", 
          fld_types={'name':"string", 'age':"integer", 'address':"string",'phone': "string",'email':'string'}, 
          init_faker=100, faker_generator = GenUserItems).do()

