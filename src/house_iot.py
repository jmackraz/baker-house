#! /usr/bin/env python
# aws IoT device-side handler
#
import logging
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
poll_hub_interval = 5
useWebsocket = False
hubEndpoint="http://localhost:6543/"
#controlPath = "receiver/mock-control"
controlPath = "receiver/control"

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
        #pretty_json = json.dumps(payload['state'], indent=2, sort_keys=True)
        pretty_json = json.dumps(payload, indent=2, sort_keys=True)
        log.info("Received a delta message. status: %s payload: %s", responseStatus, pretty_json)


        try:
            ret = requests.put(hubEndpoint+controlPath, json=payload['state'])
            if ret.status_code == 200:
                log.info("updated hub service: %s", ret.json())

                update_from_hub = ret.json()

                # remove this key before updating Thing
                last_modify = update_from_hub.pop('hub-last-modify', None)

                # acknowledge that the state change had effect
                response_payload = {'state': {'reported': update_from_hub}}
                self.shadow_handler.shadowUpdate(json.dumps(response_payload), None, 5)
            else:
                log.error("error from hub service code: {} results: {}".format( ret.status_code, ret.text))
        except:
            log.error("could not connect to %s", hubEndpoint)
            log.info("acknowledge settings change")
            response_payload = {'state': {'reported': payload['state']}}
            self.shadow_handler.shadowUpdate(json.dumps(response_payload), None, 5)
            self.shadow_handler.shadowUpdate(json.dumps(payload['state']), None, 5)



class PollingDaemon:
    def __init__(self, interval, shadow_handler):
        self.polling_interval = interval
        self.shadow_handler = shadow_handler

        self.hub_last_modify = None

    def poll(self):
        """poll the source of truth"""
        log.debug("poll source of truth")
        try:
            ret = requests.get(hubEndpoint+controlPath)
            if ret.status_code == 200:
                log.debug("data polled from hub service: %s", ret.json())

                polled_state = ret.json()
                
                if polled_state.get('hub-last-modify', self.hub_last_modify) != self.hub_last_modify:
                    log.info("data polled from hub has changed, so update Thing")

                    # remove this key before updating Thing
                    self.hub_last_modify = polled_state.pop('hub-last-modify', None)
                    response_payload = {'state': {'reported': polled_state}}

                    self.shadow_handler.shadowUpdate(json.dumps(response_payload), None, 5)
                else:
                    log.debug("data not changed")
            else:
                log.error("error from hub service code: {} results: {}".format( ret.status_code, ret.text))
        except:
            log.error("could not connect to %s", hubEndpoint)



    def goPoll(self):
        while True:
            self.poll()
            time.sleep(self.polling_interval)

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

poller = PollingDaemon(poll_hub_interval, shadow_handler)

# poll the source of truth
poller.goPoll()
