import sys
import logging
from .common import logger
from threading import Lock

print (logger.level)

def set_color(org_string, level=None):
    color_levels = {
        10: "\033[36m{}\033[0m",       # DEBUG
        20: "\033[32m{}\033[0m",       # INFO
        30: "\033[33m{}\033[0m",       # WARNING
        40: "\033[31m{}\033[0m",       # ERROR
        50: "\033[7;31;31m{}\033[0m"   # FATAL/CRITICAL/EXCEPTION
    }
    if level is None:
        return color_levels[20].format(org_string)
    else:
        return color_levels[int(level)].format(org_string)

logger.info(set_color("test"))
logger.debug(set_color("test", level=10))
logger.warning(set_color("test", level=30))
logger.error(set_color("test", level=40))
logger.fatal(set_color("test", level=50))


sa_lock = Lock()
__srv_log=None

def log_info(mess, dbg=True, ):
    def salog(pat="SA:"):
        global __srv_log
        if __srv_log: # and isinstance( __srv_log, logging.Logger ):
           return __srv_log
        hs= [e for e in logging.root.manager.loggerDict if e.startswith(pat) ]
        if len(hs) == 0:
            return logger

        sa_lock.acquire()
        __srv_log = logging.getLogger(hs[0])
        sa_lock.release()


        
        return __srv_log
    dbg and salog().info(str(mess))

log_warn=log_info    
log_debug=log_info    


def cprint(mess="mess", color="green", dbg=True, to_file=True):
    c_fmt = "--- {}"
    if sys.stdout.isatty() == True:
        c = {
            "red": "\033[91m {}\033[00m",
            "green": "\033[92m {}\033[00m",
            "yellow": "\033[93m {}\033[00m",
            "cyan": "\033[96m {}\033[00m",
            "gray": "\033[97m {}\033[00m",
            "purple": "\033[95m {}\033[00m",
        }
        c_fmt = c.get(color, c_fmt)
    if to_file == False:    
        dbg and print(c_fmt.format(str(mess)))
    else:
        dbg and log_info(str(mess))


