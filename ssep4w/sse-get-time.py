#!/usr/bin/env python

import concurrent.futures

from random import randint
from time import sleep

import sseclient

import os

from datetime import datetime
startTime = datetime.now()




this_dir = os.path.dirname(os.path.abspath(__file__)).split('/')
APP_NAME = this_dir[-1]

sqrt_url = 'http://localhost:8000/%s/sse_time_data' % APP_NAME
#sqrt_url = 'http://localhost:8000/%s/stream_sqrt_data' % APP_NAME


URLS = [ sqrt_url for e in range( 10000)  ]

# Retrieve a single page and report the URL and contents
def load_url(url, timeout):


     messages = sseclient.SSEClient( url  )
     for msg in messages:
            sleep(randint(1,5)/10.0)
            return str(msg.data)


# We can use a with statement to ensure threads are cleaned up promptly

sse_results=[]


# in server_adapters
#  pool = ThreadPoolExecutor(max_workers=4000)
#


exception_list = []
exception_count = 0
ok_count = 0


with concurrent.futures.ThreadPoolExecutor( max_workers = 20  ) as executor:
    print('max_workers: ', executor._max_workers)
    # Start the load operations and mark each future with its URL
    future_to_url = {executor.submit(load_url, url, 60): url for url in URLS}
    num = 0
    for future in concurrent.futures.as_completed(future_to_url):
        url = future_to_url[future]
        try:
            data = future.result()
            sse_results.append(  data )
        except Exception as exc:
            err_str = '%r generated an exception: %s  %s' % (url, exc, str(num))
            print (err_str)
            exception_count += 1
            
        else:
            if data:
                print('%r sse-data is %s, %s' % (url, data, str(num)))
                ok_count += 1
        num += 1


print ( len( sse_results ) )

print (f'ok_count={ok_count}, exception_count={exception_count}')
print(datetime.now() - startTime)

