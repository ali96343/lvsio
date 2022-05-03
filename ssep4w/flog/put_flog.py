#!/usr/bin/env python


"""
the script writes flog.log file
"""

import logging 
from  time  import sleep
import os

this_dir = os.path.dirname(os.path.abspath(__file__))
LOGFILE = os.path.join(this_dir, "flog.log")


logger = logging.getLogger('log_app')
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler(LOGFILE)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

def write_log_file():
    i = 0
    while True:
        logger.info(f"log message num: {i}")
        i += 1
        sleep(0.3)

if '__name__' == '__main__':
     write_log_file()
