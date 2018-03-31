#!/bin/bash
# use AWS CLI to talk to our IoT Thing in the Sky


#aws iot-data publish \
#    --topic "sdk/test/Python" \
#    --qos 1 \
#    --payload '{"message": "i poke you", "other": 393}'
#


aws iot-data update-thing-shadow \
    --thing-name $BAKERHOUSE_IOT_THING \
    --payload '{ "state": { "desired" : { "color" : { "r" : 44 } } } }' \
    /tmp/thing_shadow_out && cat /tmp/thing_shadow_out

    #--payload '{ "state": { "desired" : { "color" : { "r" : 10 }, "engine" : "ON" } } }' \
