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


print("\ntest GET")
ret = requests.get(url('receiver/control'))
if ret.status_code == 200:
    print(ret.json())
else:
    print("error. code:", ret.status_code, "results:", ret.text)


# modify something
print("\ntest PUT")
head = {'Content-type':'application/json',
             'Accept':'application/json'}

ret = requests.put(url('receiver/control', 'PUT'), json={'input':'cd'})
if ret.status_code == 200:
    print(ret.json())
else:
    print("error. code:", ret.status_code, "results:", ret.text)

ret = requests.put(url('receiver/control', 'PUT'), json={'volume':'20'})
if ret.status_code == 200:
    print(ret.json())
else:
    print("error. code:", ret.status_code, "results:", ret.text)

