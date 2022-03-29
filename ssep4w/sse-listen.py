#!/usr/bin/env python


import sseclient
import datetime


messages = sseclient.SSEClient('http://localhost:8000/ssep4w/listen')

for msg in messages:
    print(msg,' ', datetime.datetime.now().strftime("%H:%M:%S") )

