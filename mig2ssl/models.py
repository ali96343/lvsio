from .common import db, Field, Tags, groups
from pydal.validators import *
from py4web.utils.populate import populate
from yatl.helpers import SPAN, H6
import datetime, json

#import pydal
#from py4web import *
#from apps.myapp.models import db
#if not len( db().select(db.auth_user.id) ):

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

db.define_table(
    'test_table',
    Field( 'f0', 'string', label='l0'),
    Field( 'f1', 'string', label='l1'),
    Field( 'f2', 'string', label='l2'),
    )
db.commit()

if not db(db.test_table).count():
    populate(db.test_table, n=50)
    db.commit()

#db.define_table( 'uploaded_files',
#    Field('orig_file_name', requires=IS_NOT_EMPTY(),  ),
#    Field("remark",'text',),
#    Field('uniq_file_name', requires=IS_NOT_EMPTY(),  ),
#    Field('time', 'datetime', editable=False, default = datetime.datetime.now(), requires = IS_DATETIME( )),
#    )
#db.commit()

db.define_table( 'sio_user_log',
    Field('username',  ),
    Field('inout',),
    Field("orig_e",),
    Field("room",),
    Field('time', 'datetime', editable=False, default = datetime.datetime.now(), requires = IS_DATETIME( )),
    )
db.commit()

#db.define_table( 'user_data',
#    Field('username_id', requires=IS_NOT_EMPTY(),  ),
#    Field('name', 'text', requires=IS_NOT_EMPTY(),  ),
#    Field('data', 'json', requires=IS_NOT_EMPTY(),  ),
#    )
#db.commit()

#db.user_data.data.filter_in = lambda obj: json.dumps(obj)
#db.user_data.data.filter_out = lambda txt: json.loads(txt)
#myobj = ['hello', 'world', 1, {2: 3}]
#aid = db.user_data.insert(name='myobjname', data=myobj)
#row = db.user_data[aid]

#print (row.data)
db.define_table( 'sio_user_data',
#    Field('username_id', requires=IS_NOT_EMPTY(),  ),
    Field('username', 'text', requires=IS_NOT_EMPTY(),  ),
    Field('counter', 'json', requires=IS_NOT_EMPTY(),  ),
    )
db.commit()

db.sio_user_data.counter.filter_in = lambda obj: json.dumps(obj)
db.sio_user_data.counter.filter_out = lambda txt: json.loads(txt)

mycounter = ['hello', 'world', 1, {'counter': 3}]
aid = db.sio_user_data.insert(username='myobjusername', counter=mycounter)
row = db.sio_user_data[aid]
#print (row.data)

