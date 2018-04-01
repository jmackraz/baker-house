#!/usr/bin/env python

from os import environ
import json

import boto3

thing_name = environ['BAKERHOUSE_IOT_THING']

def poke_clear():
    client=boto3.client('iot-data')
    print("poke to clear shadow response")

    doc = { 'state': { 'reported': None}}
    payload = json.dumps(doc)
    print("payload:", payload)

    client.update_thing_shadow(thingName=thing_name, payload=payload)

if __name__ == "__main__":
    poke_clear()

