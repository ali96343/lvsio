from py4web import action, request, abort, response, redirect, URL
from ..settings import APP_NAME
from ..ahelp import cprint
import sys, os, random, json, uuid, string

#from ..left_menu import l_menu

import socketio
import secrets


SECRET_LEN = int(6) # 32 for real app
SIO_RED_PARAM='redis://', 'channel_tornadoMig'

#  write_only=True,  - one way channel 
r_mgr = socketio.RedisManager(SIO_RED_PARAM[0], channel=SIO_RED_PARAM[1] ,  write_only=True, )

def update_dict(d, **kwargs):
    new = {}
    for k, v in d.items():
        if isinstance(v, dict):
            new[k] = update_dict(v, **kwargs)
        else:
            new[k] = kwargs.get(k, v)
    return new


def catch_cmd(e_nm, *args, **kwargs):
    c_name = sys._getframe().f_code.co_name
    cprint ('----------------- ' + c_name )

    _ =  [  print ( a ) for a in args ]
    _ = [ print (f"{k} = {v}" ) for k,v in kwargs.items() ]

    return None

    json_data = json.dumps({"count": kwargs["count"], "sid":kwargs["sid"], "username":kwargs['username']})
    # Each client is allocated a room automatically when it connects. Use the sid as the name of the room
    r_mgr.emit("from_do_cmd", json_data, broadcast=True, include_self=False, room=kwargs['sid'])     


def XXX_cmd(**kwargs):
    c_name = sys._getframe().f_code.co_name
    cprint ('----------------- ' + c_name )

    _ = [ print (f"{k} = {v}" ) for k,v in kwargs.items() ]

    json_data = json.dumps({"count": kwargs["count"], "sid":kwargs["sid"], "username":kwargs['username']})
    # Each client is allocated a room automatically when it connects. Use the sid as the name of the room
    r_mgr.emit("from_XXX_cmd", json_data, broadcast=True, include_self=False, room=kwargs['sid'])


def ctrl_emit(**kwargs):
    c_name = sys._getframe().f_code.co_name
    cprint ('----------------- ' + c_name )
    _ = [ print (f"{k} = {v}" ) for k,v in kwargs.items() ]
    return None    

def ctrl_call_mult(**kwargs):
    c_name = sys._getframe().f_code.co_name
    cprint ('----------------- ' + c_name )

    _ = [ print (f"{k} = {v}" ) for k,v in kwargs.items() ]
    res =  kwargs['numbers'][0] * kwargs['numbers'][1] 

    json_data = json.dumps({"result": str(res), "sid":kwargs["sid"], "username":kwargs['username']})
    #r_mgr.emit("from_ctrl_call_mult", json_data, broadcast=True, include_self=False, )     
    r_mgr.emit("from_ctrl_call_mult", json_data, broadcast=True, include_self=False, room=kwargs['sid'])     

    return f'result ctrl_call_mult {res} !!!'

def db_run(**kwargs):    
    c_name = sys._getframe().f_code.co_name
    cprint ('----------------- ' + c_name )

    return None    

    _ = [ print (f"{k} = {v}" ) for k,v in kwargs.items() ]

    cmd = kwargs['cmd']
    if cmd =='PUT':
        cprint ('its PUT')
    elif cmd =='GET' :
        cprint ('its GET')
    elif cmd =='UPDATE' :
        cprint ('its UPDATE')
    else:   
        cprint (f'db_run bad cmd: {cmd}')
    return None    

name_run = {'ctrl_emit': ctrl_emit, 'db_run': db_run, 'ctrl_call_mult':ctrl_call_mult, 'XXX_cmd': XXX_cmd }

@action("siopost123" + str(secrets.token_hex( SECRET_LEN )) , method=["POST",])
def post_dispatcher():
    c_name = sys._getframe().f_code.co_name
    cprint ('----------------- ' + c_name )

    try:
        json_data = json.loads(request.body.read())
        cprint (json_data, 'yellow')

        data=json_data['data']
        if data:
            event_name=json_data['event_name']
            data['sid'] = json_data['sid']
            for e in ['sid', 'username', 'room', ]:
                data[e] = json_data[e]
            if event_name in name_run:
                ret = name_run[event_name](**data)
                return ret if ret else f'{c_name}: ok'
            return catch_cmd(event_name, **data)
        else:   
            cprint ( c_name +  ": data-dict is None", 'red' )
            return f"{c_name}: emty data-dict"

    except (KeyError, Exception) as ex:
        print(f"ex! {c_name}:", ex)
        cprint(sys.exc_info(), 'red')
        cprint('lineno: ' + str(sys._getframe().f_lineno) , 'red')
        return f"{c_name}: bad"

    return f"{c_name}: ok"

# --------------------------------------------------------
# 
# clients = []
# 
# @socketio.on('joined', namespace='/chat')
# def joined(message):
#     """Sent by clients when they enter a room.
#     A status message is broadcast to all people in the room."""
#     # Add client to client list
#     clients.append(request.sid)
# 
#     room = session.get('room')
#     join_room(room)
# 
#     # emit to the first client that joined the room
#     emit('status', {'msg': session.get('name') + ' has entered the room.'}, room=clients[0])
