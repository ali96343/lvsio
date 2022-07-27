from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .settings import APP_NAME



_app = APP_NAME
menu_str = f'{_app}/index'
ctrl_pref = f'{APP_NAME}/'

l_menu = [
    ('Home', False, URL(menu_str), []),

    ('Func', False, '#', [ 
           ('mi1', False, URL(f'{_app}/mi1')), 
           ('upload', False, URL(menu_str)), 
           ('tlist', False,  URL(menu_str)), 
    ]),

    ('Demo', False, '#'   , [ 
           ('mi2', False, URL(f'{_app}/mi2')), 
           ('index', False, URL(menu_str)), 
           ('mi3', False, URL(f'{_app}/mi3')), 
           ('pref', False, URL( ctrl_pref + 'mi4')), 
    ]),
]
