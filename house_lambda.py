#source code for the alexa skill lambda endpoint

# THIS IS JUST A TEST LAMBDA AT THIS TIME.
# NEED TO CONVERT IT TO A PROPER ALEXA SKILL
# AND TO USE DEVICE SHADOWS

from __future__ import print_function
import logging

import boto3

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.basicConfig(format=formatter)


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)



def lambda_handler(event, context):
    log.info( "lambda mia! that's one spice meatballa!")
    client = boto3.client('iot-data')
    response = client.publish( topic='sdk/test/Python', qos=1, payload='{"message": "eat me"}')
    log.debug("context: %s", context)
    log.debug("response: %s", response)

