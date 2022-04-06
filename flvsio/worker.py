#!/usr/bin/env python3
# worker.py

import os, sys
from shutil import which

import time
import requests
from celery import Celery, Task

import requests
from datetime import datetime
import socketio

#this_dir = os.path.dirname( os.path.abspath(__file__) )
#if not this_dir in sys.path:
#    sys.path.insert(0,  this_dir )

from . import chan_conf as C

from .common import settings, db, Field

# https://matthewminer.com/2015/02/21/pattern-for-async-task-queue-results

#r_mgr = socketio.RedisManager(C.r_url, write_only=True, channel=C.sio_channel)

# https://romanvm.pythonanywhere.com/post/running-multiple-celery-beat-instances-one-python-project-37/


class NotifierTask(Task):
    """Task that sends notification on completion."""

    abstract = True

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        data = {"clientid": kwargs["clientid"], "result": retval}
        requests.post( C.longtask_post  , data=data)


# >>> r = requests.post('http://httpbin.org/post', json={"key": "value"})
# >>> r.status_code
# >>> r.json()


r_mgr = socketio.RedisManager(C.r_url, write_only=True, channel=C.sio_channel)

#broker = "redis://localhost:6379/30"


MODULE = os.path.basename(__file__).replace('.py','')

app = Celery(f'{C.APPS_DIR}.{C.P4W_APP}.{MODULE}', broker = C.longtask_broker)


@app.task(base=NotifierTask)
def longtask_mytask(clientid=None, tbl='Longtask', _id = '1'):

    data_str = datetime.now().strftime("%H:%M:%S.%f") 
    data_dict = {'f0': data_str}
    some_id = int(_id)
    ev_name = sys._getframe().f_code.co_name

    try:
        db._adapter.reconnect()
        db(db[tbl].id == some_id).update(**db[tbl]._filter_fields(data_dict))
        db.commit()
    except:
        db.rollback()
        print (f'{ev_name} rollback! ')
     
    r_mgr.emit('longtask_begin', data_str , room=clientid )


    """Simulates a slow computation."""
    time.sleep(5)

    res='X'
    try:
        db._adapter.reconnect()
        r = db(db[tbl].id == some_id).select().first()
        res = [
            f"{k}={v}"
            for k, v in r.items()
            if not k in ("update_record", "delete_record")
        ]
        msg = "{}.select:  {}".format(tbl, " ".join(res))
    except Exception as ex:
        # print(sys.exc_info())
        ex_info = str(sys.exc_info()[0]).split(" ")[1].strip(">").strip("'")
        msg = f"!!! error in {ev_name}, id={some_id}, table={tbl}" + ex_info
        db.rollback()

    r_mgr.emit('longtask_end', msg , room=clientid )

    return f'42 {res}'

# 
# if __name__ == "__main__":
# 
#     path_list = os.path.abspath(__file__).split('/')
# 
#     MODULE = os.path.splitext(path_list[-1])[0]
# 
#     P4W_APP = path_list[-2] 
#     APPS_DIR = path_list[-3] 
#     P4W_DIR = "/".join(path_list[:-3])
# 
#     cmd = f"celery -A {APPS_DIR}.{P4W_APP}.{MODULE} worker -l info"
# 
#     if not which('celery'):
#         sys.exit(f'stopped! can not find celery in PATH')
# 
#     os.chdir(P4W_DIR)
#     os.system(cmd)
# 
# #    import subprocess
# #    proc = subprocess.Popen(cmd.split(),)
# #    print("PID:", proc.pid)
