#!/usr/bin/env python

import requests
import json
import time

_endpoint="http://localhost:6543/"

def url(path, method='GET'):
    url= _endpoint + path
    print(method, "url:", url)
    return url

#print("\ntest discovery")
#ret = requests.get(url('receiver'))
#if ret.status_code == 200:
#    print(ret.json())
#else:
#    print("error. code:", ret.status_code, "results:", ret.text)


print("\ntest get")
ret = requests.get(url('receiver/control'))
if ret.status_code == 200:
    print(ret.json())
else:
    print("error. code:", ret.status_code, "results:", ret.text)


## modify something
#print("\ntest put")
#head = {'Content-type':'application/json',
#             'Accept':'application/json'}
#
#ret = requests.put(url('receiver/control', 'PUT'), json={'volume':10})
#if ret.status_code == 200:
#    print(ret.json())
#else:
#    print("error. code:", ret.status_code, "results:", ret.text)
#
