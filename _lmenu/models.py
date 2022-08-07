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

db.define_table( 'uploaded_files',
    Field('orig_file_name', requires=IS_NOT_EMPTY(),  ),
    Field("remark",'text',),
    Field('uniq_file_name', requires=IS_NOT_EMPTY(),  ),
    Field('time', 'datetime', editable=False, default = datetime.now(), requires = IS_DATETIME( )),
    )

db.commit()


