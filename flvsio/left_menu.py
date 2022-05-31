from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .settings import APP_NAME

from py4web.utils.url_signer import URLSigner


from .common import (
    db,
    session,
)

#signed_url = URLSigner(session, lifespan=3600)

_app = APP_NAME
menu_str = f'{_app}/index'

l_menu = [
    ('Home', False, URL(menu_str), []),

    ('Func', False, '#', [ 
           ('admin', False, URL(f'{_app}/index')), 
           ('upload', False, URL(menu_str)), 
           ('tlist', False,  URL(f'{_app}/tlist_ul', )), 
    ]),

    ('Demo', False, '#'   , [ 
           ('index', False, URL(menu_str)), 
           ('index', False, URL(menu_str)), 
           ('index', False, URL(menu_str)), 
    ]),
]
