#!/bin/bash
# use AWS CLI to talk to our IoT Thing in the Sky


aws iot-data publish \
    --topic "sdk/test/Python" \
    --qos 1 \
    --payload '{"message": "i poke you", "other": 393}'

