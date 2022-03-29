import queue

class MessageAnnouncer:

    def __init__(self):
        self.listeners = []

    def listen(self):
        self.listeners.append(queue.Queue(maxsize=5))
        return self.listeners[-1]

    def announce(self, msg):
        # We go in reverse order because we might have to delete an element, which will shift the
        # indices backward
        print (msg)
        print (len(self.listeners)  )
        #for i in reversed(range(len(self.listeners))):
        for i in range(len(self.listeners)):
            print (i)
            try:
                self.listeners[i].put_nowait(msg)
            except queue.Full:
                del self.listeners[i]
        print (self.listeners)



announcer = MessageAnnouncer()

def format_sse(data: str, event=None) -> str:
    msg = f'data: {data}\n\n'
    if event is not None:
        msg = f'event: {event}\n{msg}'
    return msg

msg = format_sse(data='pong')
announcer.announce(msg=msg)

messages  = announcer.listeners  
print ( messages )

