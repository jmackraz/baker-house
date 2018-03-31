#! /usr/bin/env python
# aws IoT device-side handler
#
import logging
import time
import argparse
import json
from os import environ

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient, AWSIoTMQTTShadowClient


# config from environment
host = environ["BAKERHOUSE_ENDPOINT"]
certificatePath = environ["BAKERHOUSE_MYCERT_FILE"]
rootCAPath = environ["BAKERHOUSE_ROOTCERT_FILE"]
privateKeyPath = environ["BAKERHOUSE_PRIVATEKEY_FILE"]
thingName = environ["BAKERHOUSE_IOT_THING"]
clientId = "basicPubSub"
topic = "sdk/test/Python"
poll_hub_interval = 10000

useWebsocket = False
shadowTopicSubscribe = False

# system mqtt topics used by device shadow (diagnostics/education)
#
device_shadow_topics = [
    "$aws/things/{}/shadow/update/accepted",
    "$aws/things/{}/shadow/update/rejected",
    "$aws/things/{}/shadow/update/delta",
    "$aws/things/{}/shadow/get/accepted",
    "$aws/things/{}/shadow/get/rejected",
    "$aws/things/{}/shadow/delete/accepted",
    "$aws/things/{}/shadow/delete/rejected",
    "$aws/things/{}/shadow/update/documents",
    ]

# logging
log = logging.getLogger("house_iot")
log.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
#formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
log.addHandler(streamHandler)

### ###

# Custom MQTT message callback
def subscribeCallback(client, userdata, message):
    parsed = json.loads(message.payload)
    pretty_json = json.dumps(parsed, indent=2, sort_keys=True)
    #log.info("message received from topic %s: %s", message.topic, pretty_json)
    log.info("message received from topic %s", message.topic)


shadow_client = None
if useWebsocket:
    mqtt_client = AWSIoTMQTTClient(clientId, useWebsocket=True)
    mqtt_client.configureEndpoint(host, 443)
    mqtt_client.configureCredentials(rootCAPath)

    shadow_client = AWSIoTMQTTShadowClient(clientId, useWebsocket=True)
    shadow_client.configureEndpoint(host, 443)
    shadow_client.configureCredentials(rootCAPath)
else:
    mqtt_client = AWSIoTMQTTClient(clientId)
    mqtt_client.configureEndpoint(host, 8883)
    mqtt_client.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

    shadow_client = AWSIoTMQTTShadowClient(clientId)
    shadow_client.configureEndpoint(host, 8883)
    shadow_client.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# connection configuration from AWS sample
shadow_client.configureAutoReconnectBackoffTime(1, 32, 20)
shadow_client.configureConnectDisconnectTimeout(10)  # 10 sec
shadow_client.configureMQTTOperationTimeout(5)  # 5 sec
shadow_client.connect()

# pubsub stuff
mqtt_client.configureAutoReconnectBackoffTime(1, 32, 20)
mqtt_client.configureConnectDisconnectTimeout(10)  # 10 sec
mqtt_client.configureMQTTOperationTimeout(5)  # 5 sec
mqtt_client.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
mqtt_client.configureDrainingFrequency(2)  # Draining: 2 Hz
mqtt_client.connect()


class ShadowCallback:
    def __init__(self):
        pass

    def delta(self, payload_json, responseStatus, token):
        payload = json.loads(payload_json)
        #pretty_json = json.dumps(payload['state'], indent=2, sort_keys=True)
        pretty_json = json.dumps(payload, indent=2, sort_keys=True)
        log.info("Received a delta message: %s", pretty_json)

        #newPayload = '{"state":{"reported":' + deltaMessage + '}}'
        #self.deviceShadowInstance.shadowUpdate(newPayload, None, 5)


shadow_handler = shadow_client.createShadowHandlerWithName(thingName, True)
shadow_callback = ShadowCallback()
shadow_handler.shadowRegisterDeltaCallback(shadow_callback.delta)


#mqtt_client = shadow_client.getMQTTConnection()

mqtt_client.subscribe(topic, 1, subscribeCallback)

if shadowTopicSubscribe:
    for topic in device_shadow_topics:
        mqtt_client.subscribe(topic.format(thingName), 1, subscribeCallback)
        

log.info("connected")

# poll the source of truth
while True:
    time.sleep(poll_hub_interval)
    log.debug("poll source of truth")
    #message = {}
    #message['message'] = args.message
    #message['sequence'] = loopCount
    #messageJson = json.dumps(message)
    #mqtt_client.publish(topic, messageJson, 1)
