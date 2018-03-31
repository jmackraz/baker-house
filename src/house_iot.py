#! /usr/bin/env python
# aws IoT device-side handler
#
import logging
import time
import argparse
import json
from os import environ

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient

# config from environment
host = environ["BAKERHOUSE_ENDPOINT"]
certificatePath = environ["BAKERHOUSE_MYCERT_FILE"]
rootCAPath = environ["BAKERHOUSE_ROOTCERT_FILE"]
privateKeyPath = environ["BAKERHOUSE_PRIVATEKEY_FILE"]
thingName = environ["BAKERHOUSE_IOT_THING"]

clientId = "house_iot"
poll_hub_interval = 10000
useWebsocket = False


# logging
log = logging.getLogger("house_iot")
log.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
#formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
log.addHandler(streamHandler)

### ###
# Events and polling

class ShadowCallback:
    """device callbacks"""
    def __init__(self, shadow_handler):
        log.debug("ShadowCallback init")
        self.shadow_handler = shadow_handler

    def delta(self, payload_json, responseStatus, token):
        payload = json.loads(payload_json)
        pretty_json = json.dumps(payload['state'], indent=2, sort_keys=True)
        #pretty_json = json.dumps(payload, indent=2, sort_keys=True)
        log.info("Received a delta message: %s", pretty_json)

        # acknowledge that the state change had effect
        response_payload = {'state': {'reported': payload['state']}}

        self.shadow_handler.shadowUpdate(json.dumps(response_payload), None, 5)

class PollingDaemon:
    def __init__(self, interval):
        self.polling_interval = interval

    def poll(self):
        """poll the source of truth"""
        log.debug("poll source of truth stub")

    def goPoll(self):
        while True:
            time.sleep(self.polling_interval)
            self.poll()

### ###

shadow_client = None
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
log.info("connected")

shadow_handler = shadow_client.createShadowHandlerWithName(thingName, True)
shadow_callback = ShadowCallback(shadow_handler)
shadow_handler.shadowRegisterDeltaCallback(shadow_callback.delta)

poller = PollingDaemon(poll_hub_interval)

# poll the source of truth
poller.goPoll()
