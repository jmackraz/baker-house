#!/usr/bin/env python

from os import environ
import boto3


def get_verified_env(env_var):
    """try to make sure environment variables are set up correctly"""
    if env_var in environ and not environ[env_var].startswith("NOT"):
        return environ[env_var]
    else:
        print("the environment variable {} is not set up correctly. It's value is {}".format(env_var, environ.get(env_var)))
        exit(0)


def create_thing_type():
    thing_type = get_verified_env('BAKERHOUSE_IOT_THING_TYPE')
    client=boto3.client('iot')

    print("creating thing type:", thing_type)

    # check if it exists
    res = client.list_thing_types(thingTypeName=thing_type)
    # should contain only our thing type, if it exists
    if res['thingTypes']:
        print("Thing Type {} already exists. ARN: {}".format(thing_type, res['thingTypes'][0]['thingTypeArn']))
    else:
        print("create type...")
        res = client.create_thing_type(
                            thingTypeName=thing_type,
                            thingTypeProperties={'thingTypeDescription': "My Baker House IoT Thing Type"} )
        print("created. Info:", res)

def create_thing():
    thing_type = get_verified_env('BAKERHOUSE_IOT_THING_TYPE')
    thing_name = get_verified_env('BAKERHOUSE_IOT_THING')

    client=boto3.client('iot')

    print("creating thing:", thing_name)
    res = client.list_things(thingTypeName=thing_type)
    #print("list_things:", res)
    
    for thing in res['things']:
        if thing['thingName'] == thing_name:
            print("Thing {} already exists. ARN: {}".format(thing_name, res['things'][0]['thingArn']))
            return

    print("create thing...")
    res = client.create_thing(
                        thingName=thing_name,
                        thingTypeName=thing_type )
    print("created. Info:", res)

def create_policy():
    """create AWS IoT policy for my thing"""
    policy_name = get_verified_env('BAKERHOUSE_IOT_THING_POLICY')
    client=boto3.client('iot')

    res = client.list_policies()
    #print("policies:", res)
    for policy in res['policies']:
        if policy['policyName'] == policy_name:
            print("Policy {} already exists. ARN: {}".format(policy_name, policy['policyArn']))
            return

    policy_document = '{"Version": "2012-10-17", "Statement": [ {  "Effect": "Allow", "Action": "iot:*", "Resource": "*" } ]}'
    res = client.create_policy(policyName=policy_name, policyDocument=policy_document)
    #print("created policy:", res)
    print("created policy {}. ARN: {}".format(policy_name, res['policyArn']))


if __name__ == "__main__":
    #create_thing_type()
    #create_thing()
    create_policy()

