from py4web import action, request, abort, response, redirect, URL
from ..common import db, session, T, cache #, auth, logger, authenticated, unauthenticated, flash
from ..settings import APP_NAME
from ..ahelp import cprint
import sys, os, random, json, uuid, string

# from ..left_menu import l_menu

import socketio
import secrets

from ..ahelp import log_info 


SECRET_LEN = int(6)  # 32 for real app
SIO_RED_PARAM = "redis://", "channel_tornadoMig"

#  write_only=True,  - one way channel
r_mgr = socketio.RedisManager(
    SIO_RED_PARAM[0],
    channel=SIO_RED_PARAM[1],
    write_only=True,
)


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
    cprint(f"----------------- {c_name}")

    _ = [cprint(a) for a in args]
    _ = [cprint(f"{k} = {v}") for k, v in kwargs.items()]


    return None

    json_data = json.dumps(
        {"count": kwargs["count"], "sid": kwargs["sid"], "username": kwargs["username"]}
    )
    # Each client is allocated a room automatically when it connects. Use the sid as the name of the room
    r_mgr.emit( "from_do_cmd", json_data, broadcast=True, include_self=False, room=kwargs["sid"])


def xxx_cmd(**kwargs):
    c_name = sys._getframe().f_code.co_name
    cprint(f"----------------- {c_name}")

    _ = [cprint(f"{k} = {v}") for k, v in kwargs.items()]

    json_data = json.dumps( {"count": kwargs["count"], "sid": kwargs["sid"], "username": kwargs["username"]})
    # Each client is allocated a room automatically when it connects. Use the sid as the name of the room
    r_mgr.emit( "from_xxx_cmd", json_data, broadcast=True, include_self=False, room=kwargs["sid"],)


def ctrl_emit(**kwargs):
    c_name = sys._getframe().f_code.co_name
    cprint(f"----------------- {c_name}")
    _ = [cprint(f"{k} = {v}") for k, v in kwargs.items()]
    return None


def ctrl_call_mult(**kwargs):
    c_name = sys._getframe().f_code.co_name
    cprint(f"----------------- {c_name}")

    _ = [cprint(f"{k} = {v}") for k, v in kwargs.items()]
    res = kwargs["numbers"][0] * kwargs["numbers"][1]

    json_data = json.dumps(
        {"result": str(res), "sid": kwargs["sid"], "username": kwargs["username"]}
    )
    # r_mgr.emit("from_ctrl_call_mult", json_data, broadcast=True, include_self=False, )
    r_mgr.emit( "from_ctrl_call_mult", json_data, broadcast=True, include_self=False, room=kwargs["sid"],)

    return f"result ctrl_call_mult {res} !!!"


def db_run(**kwargs):
    c_name = sys._getframe().f_code.co_name
    cprint(f"----------------- {c_name}")

    _ = [cprint(f"{k} = {v}", 'yellow') for k, v in kwargs.items()]

    log_info(f'salog: {c_name}')

    cmd = kwargs["cmd"]
    if cmd == "PUT":
        puttbl = db[ kwargs['table'] ]
        aid = puttbl.insert(**puttbl._filter_fields(kwargs) )
        if aid:
            db.commit()
            cprint (aid)
        cprint("its PUT")
    elif cmd == "GET":
        gettbl = db[ kwargs['table'] ]
        xid = int( kwargs['id'] )
        tblrow =  db( gettbl.id  == xid  ).select() 
        #tblrow = gettbl(xid )
        if tblrow:
            cprint (f"{xid} {tblrow.as_list()}")
            #return tblrow.as_dict()
            return tblrow.as_list()
        cprint("its GET")
    elif cmd == "UPDATE":
        updatetbl = db[ kwargs['table'] ]
        xid = int( kwargs['id'] )
        res = db(updatetbl.id== xid).update(**kwargs)
        if res ==1:
            db.commit()
            cprint (f"{xid} updated")
        cprint("its UPDATE")
    elif cmd == "DEL":
        cprint("its DEL")
        deltbl = db[ kwargs['table'] ]
        xid = int( kwargs['id'] )
        res = db(deltbl.id  == xid ).delete()
        if res == 1: # one record deleted
            db.commit()
            cprint (f"{xid} deleted")
        cprint("its DEL")
    else:
        cprint(f"db_run: bad {cmd}",'red')
    return None


name_run = {
    "ctrl_emit": ctrl_emit,
    "db_run": db_run,
    "ctrl_call_mult": ctrl_call_mult,
    "xxx_cmd": xxx_cmd,
}


@action( "siopost123" + str(secrets.token_hex(SECRET_LEN)), method=[ "POST", ],)
def post_dispatcher():
    c_name = sys._getframe().f_code.co_name
    cprint(f"----------------- {c_name}")

    try:
        json_data = json.loads(request.body.read())
        cprint(json_data, "yellow")

        data = json_data["data"]
        if data:
            event_name = json_data["event_name"]
            data["sid"] = json_data["sid"]
            for e in [ "sid", "username", "room", ]:
                data[e] = json_data[e]

            try:    
                ret = name_run[event_name](**data)
            except KeyError:    
                ret = catch_cmd(event_name, **data)
            return ret if ret else f"{c_name}: ok"

        else:
            cprint( f"{c_name}: emty data-dict", 'red' )
            return f"{c_name}: emty data-dict"

    except (KeyError, Exception) as ex:
        cprint(f"ex! {c_name}:  {ex}")
        cprint(sys.exc_info(), "red")
        cprint("lineno: " + str(sys._getframe().f_lineno), "red")
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
