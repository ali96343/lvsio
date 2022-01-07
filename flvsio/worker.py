#!/usr/bin/env python3
# worker.py


import time
import requests
from celery import Celery, Task

import requests

# https://matthewminer.com/2015/02/21/pattern-for-async-task-queue-results


class NotifierTask(Task):
    """Task that sends notification on completion."""

    abstract = True

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        url = "http://localhost:8000/flvsio/longtask_notify"
        data = {"clientid": kwargs["clientid"], "result": retval}
        requests.post(url, data=data)


# >>> r = requests.post('http://httpbin.org/post', json={"key": "value"})
# >>> r.status_code
# >>> r.json()

broker = "redis://localhost:6379/30"
app = Celery(__name__, broker=broker)


@app.task(base=NotifierTask)
def mytask(clientid=None):
    """Simulates a slow computation."""
    time.sleep(5)
    return 42


if __name__ == "__main__":

    import os, sys
    from shutil import which

    path_list = os.path.abspath(__file__).split('/')

    MODULE = os.path.splitext(path_list[-1])[0]

    P4W_APP = path_list[-2] 
    APPS_DIR = path_list[-3] 
    P4W_DIR = "/".join(path_list[:-3])

    cmd = f"celery -A {APPS_DIR}.{P4W_APP}.{MODULE} worker -l info"

    if not which('celery'):
        sys.exit(f'stopped! can not find celery in PATH')

    os.chdir(P4W_DIR)
    os.system(cmd)

#    import subprocess
#    proc = subprocess.Popen(cmd.split(),)
#    print("PID:", proc.pid)
