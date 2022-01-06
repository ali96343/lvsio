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
        url = 'http://localhost:8000/flvsio/longtask_notify'
        data = {'clientid': kwargs['clientid'], 'result': retval}
        requests.post(url, data=data)
#>>> r = requests.post('http://httpbin.org/post', json={"key": "value"})
#>>> r.status_code
#>>> r.json()

broker = 'redis://localhost:6379/30'
app = Celery(__name__, broker=broker)

@app.task(base=NotifierTask)
def mytask(clientid=None):
    """Simulates a slow computation."""
    time.sleep(5)
    return 42

