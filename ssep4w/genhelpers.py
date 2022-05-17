from py4web import action, request, response, abort, redirect, URL
import threading
import inspect 
import ctypes



# some flask-function

def fjsonify( data={}, status=200  ):
    response.headers["Content-Type"] = "application/json"
    response.status= int(status)
    return json.dumps(data)

def freturn( data="hi!", status = 200 ):
    response.status= int(status)
    return data

# ---------------------------------------------------------------------------
libc = ctypes.cdll.LoadLibrary('libc.so.6')

# System dependent, see e.g. /usr/include/x86_64-linux-gnu/asm/unistd_64.h
SYS_gettid = 186

def getThreadId():
   """Returns OS thread id - Specific to Linux"""
   return libc.syscall(SYS_gettid)


# https://stackoverflow.com/questions/1095543/get-name-of-calling-functions-module-in-python
def info(msg='mod.__name__'):
    frm = inspect.stack()[1]
    mod = inspect.getmodule(frm[0])
    print( '     [%s] %s' % (mod.__name__, msg) )


def worker_info():
    print ( f"========== {sys._getframe().f_code.co_name}" ) 

    #print (sys._current_frames().values() )
    f = list(sys._current_frames().values())[0]
    print ("    ",f.f_back.f_globals['__file__'] )
    print ("    ", f.f_back.f_globals['__name__'] )
    getframe_expr = "sys._getframe({}).f_code.co_name"
    caller = eval(getframe_expr.format(2))
    callers_caller = eval(getframe_expr.format(3))
    print(" --  called from: ", caller)
    print("    ", caller, "was called from: ", callers_caller, "--")

    print("     name:  ",threading.current_thread().name)
    print("     ident: ",threading.get_ident())
    print("     sys-ident: ",getThreadId())
    _ = [     print('           ',thread.name) for thread in threading.enumerate() ]

# --------------------------------------------------------------
# https://anyio.readthedocs.io/en/stable/threads.html

from anyio import to_thread, run


async def main():
    await to_thread.run_sync(sleep, 0.5)
    print ('xxxxxx')

#run(main)



class XSafeList:
    def __init__(self):
        self._list = list()
        self._lock = Lock()

    def append(self, value):
        with self._lock:
            self._list.append(value)

    def check(self, value):
        with self._lock:
            return value in self._list

    def remove(self, value):
        with self._lock:
            self._list.remove(value)

    def pop(self):
        with self._lock:
            return self._list.pop()

    def get(self, index):
        with self._lock:
            return self._list[index]

    def __call__(self):
        with self._lock:
            return self._list

    @property
    def all(self):
        with self._lock:
            return self._list

    def length(self):
        with self._lock:
            return len(self._list)


# custom class wrapping a list in order to make it thread safe
class SafeList:
    # constructor
    def __init__(self):
        self._list = list()
        self._lock = threading.Lock()

    # add a value to the list
    def append(self, value):
        with self._lock:
            self._list.append(value)

    # search value in list
    def check(self, value):
        with self._lock:
            return value in self._list

    def remove(self, value):
        with self._lock:
            # append the value
            self._list.remove(value)

    # remove and return the last value from the list
    def pop(self):
        with self._lock:
            return self._list.pop()

    # read a value from the list at an index
    def get(self, index):
        # acquire the lock
        with self._lock:
            # read a value at the index
            return self._list[index]

    def __call__(self):
        with self._lock:
            return self._list

    @property
    def all(self):
        with self._lock:
            return self._list

    # return the number of items in the list
    def length(self):
        # acquire the lock
        with self._lock:
            return len(self._list)

# ----------------------------------------
# https://gist.github.com/platdrag/e755f3947552804c42633a99ffd325d4

class threadsafe_iter:
    """Takes an iterator/generator and makes it thread-safe by
    serializing call to the `next` method of given iterator/generator.
    """

    def __init__(self, it):
        self.it = it
        self.lock = threading.Lock()

    def __iter__(self):
        return self

    def __next__(self):
        with self.lock:
            return self.it.__next__()


def threadsafe_generator(f):
    """A decorator that takes a generator function and makes it thread-safe."""

    def g(*a, **kw):
        return threadsafe_iter(f(*a, **kw))

    return g

