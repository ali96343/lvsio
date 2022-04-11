#!/usr/bin/env python

import concurrent.futures

from random import randint
from time import sleep

import sseclient

import os


this_dir = os.path.dirname(os.path.abspath(__file__)).split('/')
APP_NAME = this_dir[-1]

sqrt_url = 'http://localhost:8000/%s/stream_sqrt_data' % APP_NAME


URLS = [ sqrt_url for e in range( 40)  ]

def load_url(url, timeout):


     messages = sseclient.SSEClient( url  )
     for msg in messages:
            sleep(randint(1,3)/10.0)
            return str(msg.data)



sse_results=[]


with concurrent.futures.ThreadPoolExecutor( max_workers = 20  ) as executor:
    print('max_workers: ', executor._max_workers)
    # Start the load operations and mark each future with its URL
    future_to_url = {executor.submit(load_url, url, 60): url for url in URLS}
    for future in concurrent.futures.as_completed(future_to_url):
        url = future_to_url[future]
        try:
            data = future.result()
            sse_results.append(  data )
        except Exception as exc:
            print('%r generated an exception: %s' % (url, exc))
        else:
            print('%r page is %s bytes' % (url, data))


print ( len( sse_results ) )


