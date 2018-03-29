#!/usr/bin/env python

import requests
import json

_endpoint="http://localhost:6543/"

def url(path):
    url= _endpoint + path
    print("url:", url)

    return url

ret = requests.get(url('receiver'))
print(ret.status_code)
print(ret.json())


ret = requests.get(url('receiver/control'))
print(ret.status_code)
print(ret.json())

head = {'Content-type':'application/json',
             'Accept':'application/json'}


ret = requests.put(url('receiver/control'), json={'volume':33})
print(ret.status_code)
print(ret.json())
