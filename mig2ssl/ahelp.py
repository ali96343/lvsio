import sys
import logging
from .common import logger

__srv_log=None

def log_info(mess, dbg=True, ):
    def salog(pat="SA:"):
        global __srv_log
        if __srv_log: # and isinstance( __srv_log, logging.Logger ):
           return __srv_log
        hs= [e for e in logging.root.manager.loggerDict if e.startswith(pat) ]
        if len(hs) == 0:
            return logger
        __srv_log = logging.getLogger(hs[0])
        return __srv_log
    #print ('!!!!!!!!!!!!!!!!!!!!!!!!!!! ',salog().handlers) 
    #    while logger.hasHandlers():
    #        logger.removeHandler(logger.handlers[0])
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


