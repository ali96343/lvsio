#!/usr/bin/env python

import time
import requests

import os
this_dir = os.path.dirname(os.path.abspath(__file__)).split('/')
APP_NAME = this_dir[-1]


ping_url = 'http://localhost:8000/%s/ping' % APP_NAME

print ('ping_url: ', ping_url )



while True:
    requests.get(ping_url)
    time.sleep(1)


