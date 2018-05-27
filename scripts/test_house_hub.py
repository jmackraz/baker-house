#!/usr/bin/env python

import requests
import json
from time import sleep

_endpoint="http://localhost:6543/"

# don't pace commands too quickly
command_delay = 1

def url(path, method='GET'):
    url= _endpoint + path
    #print(method, "url:", url)
    return url

#print("\ntest discovery")
#ret = requests.get(url('receiver'))
#if ret.status_code == 200:
#    print(ret.json())
#else:
#    print("error. code:", ret.status_code, "results:", ret.text)



def get_state(msg):
    print("get_state:", msg)
    ret = requests.get(url('receiver/control'))
    if ret.status_code == 200:
        print(ret.json())
    else:
        print("error. code:", ret.status_code, "results:", ret.text)

def put_something(msg, payload):
    head = {'Content-type':'application/json', 'Accept':'application/json'} # unused?
    print(msg)
    ret = requests.put(url('receiver/control', 'PUT'), json=payload)
    if ret.status_code == 200:
        print(ret.json())
    else:
        print("error. code:", ret.status_code, "results:", ret.text)

    sleep(command_delay)


get_state("initial state")
put_something("power off", {'power': 'off'})
#put_something("power on", {'power': 'on'})
put_something("input cd", {'input': 'cd'})
put_something("volume 20", {'volume': '20'})
put_something("volume 23", {'volume': '23'})

get_state("final state")

