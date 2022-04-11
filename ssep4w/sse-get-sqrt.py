#!/usr/bin/env python


import sseclient
import urllib3
import requests


import os
this_dir = os.path.dirname(os.path.abspath(__file__)).split('/')
APP_NAME = this_dir[-1]


sqrt_url = 'http://localhost:8000/%s/stream_sqrt_data' % APP_NAME

print ('sqrt_url: ', sqrt_url )



messages = sseclient.SSEClient( sqrt_url  )
for msg in messages:
            print(msg.data)

