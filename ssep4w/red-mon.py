import os
import redis
import json

from multiprocessing import Process

redis_conn = redis.Redis(charset="utf-8", decode_responses=True)

RED_CHAN = "monit"


def sub(name: str):
   pubsub = redis_conn.pubsub()
   pubsub.subscribe( RED_CHAN  )
   for message in pubsub.listen():
       if message.get("type") == "message":
           #print (message)
           data = json.loads(message.get("data"))
           #print("%s : %s" % (name, data))

           msg = data.get("msg")
           from_ = data.get("from")
           to = data.get("to")
           time_ = data.get("time")
           id_=data.get('id')
           now=data.get('now')

           msg = dict(from_=from_, msg=msg, id=id_,  to=to, time=time_, now=now )
           print( msg )


if __name__ == "__main__":
   Process(target=sub, args=("reader1",)).start()


