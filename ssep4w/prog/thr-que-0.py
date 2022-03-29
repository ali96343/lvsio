import queue
import threading
import time

fifo_queue = queue.Queue()

lock = threading.RLock()


def hd():
    with lock:
        print("hi")
        time.sleep(1)
        print("done")


for i in range(3):
    cc = threading.Thread(target=hd)
    fifo_queue.put(cc)
    cc.start()

