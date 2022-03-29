#!/usr/bin/env python


import sseclient
import datetime


import os
this_dir = os.path.dirname(os.path.abspath(__file__)).split('/')
APP_NAME = this_dir[-1]


listen_url = 'http://localhost:8000/%s/listen' % APP_NAME

print ('listen_url: ', listen_url )



messages = sseclient.SSEClient( listen_url  )

for msg in messages:
    print(msg,' ', datetime.datetime.now().strftime("%H:%M:%S") )

