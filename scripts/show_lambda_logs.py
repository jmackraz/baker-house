#! /usr/bin/env python

# print last N seconds of CloudWatch log messages for our lambda

import os
from os import environ
import time
from datetime import datetime
from datetime import timedelta
import json
import boto3

log_group_name="/aws/lambda/ask-custom-baker-house-jim-dev"
# ZZZ: need to fetch or construct this

#num_seconds = 60
num_seconds = 60 * 60 * 10

secs_since_epoch = time.time()
start_time_sec = secs_since_epoch - num_seconds
start_time_ms = round(start_time_sec*1000)

start_datetime = datetime.fromtimestamp(start_time_sec)


print("showing logs for last {} seconds, starting at: {}:".format(num_seconds, start_datetime))
#print("now:", now)

cloudwatch_client=boto3.client('logs')

result = cloudwatch_client.filter_log_events(logGroupName=log_group_name, startTime=start_time_ms, interleaved=True)

for event in result['events']:
    print("msg: {msg}".format(msg=event['message']))
