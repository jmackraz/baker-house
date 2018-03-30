#! /usr/bin/env python
# aws IoT device-side handler
#
import logging
import time
import argparse
import json
from os import environ

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient


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
shadowTopicSubscribe = True

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
def customCallback(client, userdata, message):
    parsed = json.loads(message.payload)
    pretty_json = json.dumps(parsed, indent=2, sort_keys=True)
    log.info("message received from topic %s: %s", message.topic, pretty_json)


iotclient = None
if useWebsocket:
    iotclient = AWSIoTMQTTClient(clientId, useWebsocket=True)
    iotclient.configureEndpoint(host, 443)
    iotclient.configureCredentials(rootCAPath)
else:
    iotclient = AWSIoTMQTTClient(clientId)
    iotclient.configureEndpoint(host, 8883)
    iotclient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# connection configuration from AWS sample
iotclient.configureAutoReconnectBackoffTime(1, 32, 20)
iotclient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
iotclient.configureDrainingFrequency(2)  # Draining: 2 Hz
iotclient.configureConnectDisconnectTimeout(10)  # 10 sec
iotclient.configureMQTTOperationTimeout(5)  # 5 sec

iotclient.connect()
iotclient.subscribe(topic, 1, customCallback)

if shadowTopicSubscribe:
    for topic in device_shadow_topics:
        iotclient.subscribe(topic.format(thingName), 1, customCallback)
        

log.info("connection made")

# poll the source of truth
while True:
    time.sleep(poll_hub_interval)
    log.debug("poll source of truth")
    #message = {}
    #message['message'] = args.message
    #message['sequence'] = loopCount
    #messageJson = json.dumps(message)
    #iotclient.publish(topic, messageJson, 1)
