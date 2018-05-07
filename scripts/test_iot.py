#! /usr/bin/env python
# aws IoT device-side handler
#
import time
import json
from os import environ
import requests

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient

# config from environment
host = environ["BAKERHOUSE_ENDPOINT"]
certificatePath = environ["BAKERHOUSE_MYCERT_FILE"]
rootCAPath = environ["BAKERHOUSE_ROOTCERT_FILE"]
privateKeyPath = environ["BAKERHOUSE_PRIVATEKEY_FILE"]
thingName = environ["BAKERHOUSE_IOT_THING"]

clientId = "house_iot"
useWebsocket = False


### ###
# Events and polling

class ShadowEcho:
    """device callbacks"""
    def __init__(self, shadow_handler):
        print("ShadowEcho init")
        self.shadow_handler = shadow_handler

    def delta(self, payload_json, responseStatus, token):
        """reports updates from device shadow, and echos back consent"""
        payload = json.loads(payload_json)
        pretty_json = json.dumps(payload, indent=2, sort_keys=True)
        #print("Received a delta message. status: {} payload: {}".format(responseStatus, pretty_json))
        desired_delta = payload['state']
        print("callback: desired state:", desired_delta)

        # echo back agreement
        response_payload = {'state': {'reported': desired_delta}}
        self.shadow_handler.shadowUpdate(json.dumps(response_payload), None, 5)

if useWebsocket:
    shadow_client = AWSIoTMQTTShadowClient(clientId, useWebsocket=True)
    shadow_client.configureEndpoint(host, 443)
    shadow_client.configureCredentials(rootCAPath)
else:
    shadow_client = AWSIoTMQTTShadowClient(clientId)
    shadow_client.configureEndpoint(host, 8883)
    shadow_client.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# connection configuration from AWS sample
shadow_client.configureAutoReconnectBackoffTime(1, 32, 20)
shadow_client.configureConnectDisconnectTimeout(10)  # 10 sec
shadow_client.configureMQTTOperationTimeout(5)  # 5 sec
shadow_client.connect()
print("connected")

shadow_handler = shadow_client.createShadowHandlerWithName(thingName, True)
shadow_callback = ShadowEcho(shadow_handler)
shadow_handler.shadowRegisterDeltaCallback(shadow_callback.delta)

for volume_level in [10, 12, 14, 16, 13]:
    time.sleep(4)
    print("tell our thing that we desire volume level:", volume_level)
    response_payload = {'state': {'desired': {'volume': volume_level}}}
    shadow_handler.shadowUpdate(json.dumps(response_payload), None, 5)

print("done. waiting for callbacks")
time.sleep(5)
