#!/usr/bin/env python

import time
import requests

while True:
    requests.get('http://localhost:8000/ssep4w/ping')
    time.sleep(1)


