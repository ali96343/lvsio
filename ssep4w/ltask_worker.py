# worker.py
import time
from random import randint
from celery import Celery
import requests
from celery import Celery, Task

longtask_broker = "redis://localhost:6379/10"
app = Celery(__name__, broker= longtask_broker  )

class NotifierTask(Task):
    """Task that sends notification on completion."""
    abstract = True

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        url = 'http://localhost:8000/ssep4w/ltask/longtask_notify'
        data = {'clientid': kwargs['clientid'], 'result': retval}
        requests.post(url, data=data)

@app.task(base=NotifierTask)
def longtask_mytask(clientid=None):
    """Simulates a slow computation."""
    time.sleep(7)
    return f"42 and random: {randint(10,90)}" 

