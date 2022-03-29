import queue
import threading
import time

fifo_queue = queue.Queue()

semaphore = threading.Semaphore()


def hd():
    with semaphore:
        print("hi")
        time.sleep(1)
        print("done")


for i in range(3):
    cc = threading.Thread(target=hd)
    fifo_queue.put(cc)
    cc.start()


# https://stackoverflow.com/questions/70492568/how-to-use-queue-with-threading-properly

