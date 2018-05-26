#!/usr/bin/env python

from os import environ
import sys
import json

import boto3


thing_name = environ['BAKERHOUSE_IOT_THING']

state_json='{"input" : "directv", "volume" : 29}'

def poke(desired_state_json):

    client=boto3.client('iot-data')
    print("POKE with state:", desired_state_json)

    ## construct payload in json because we take json arg
    #format_str='{{ "state": {{ "desired" : {} }} }}'
    #payload=format_str.format(state)

    desired_state = json.loads(desired_state_json)
    doc = { 'state': { 'desired': desired_state}}
    payload = json.dumps(doc)

    print("payload:", payload)

    client.update_thing_shadow(thingName=thing_name, payload=payload)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        poke(state_json)
    elif len(sys.argv) > 1:
        poke(sys.argv[1])

