#!/usr/bin/env python

from os import environ
import os
import requests
import boto3


def get_verified_env(env_var, exit_on_fail=True):
    """try to make sure environment variables are set up correctly"""
    if not environ.get(env_var, "NOT SET").startswith("NOT"):
        return environ[env_var]
    else:
        if exit_on_fail:
            print("the environment variable {} is not set up correctly. It's value is {}".format(env_var, environ.get(env_var)))
            exit(0)
        else:
            return("INVALID ENVIRONMENT VALUE")


def create_thing_type():
    thing_type = get_verified_env('BAKERHOUSE_IOT_THING_TYPE')
    client=boto3.client('iot')
    print("\nTHING TYPE")

    # check if it exists
    res = client.list_thing_types(thingTypeName=thing_type)
    # should contain only our thing type, if it exists
    if res['thingTypes']:
        print("{} already exists".format(thing_type))
        #print("thing:", res['thingTypes'][0])
    else:
        res = client.create_thing_type(
                            thingTypeName=thing_type,
                            thingTypeProperties={'thingTypeDescription': "My Baker House IoT Thing Type"} )
        #print("created, info:", res)

    res = client.describe_thing_type(thingTypeName=thing_type)
    #print("thing type:", res)
    print("Name: {name}\nARN: {arn}\nID: {id}".format( name=res['thingTypeName'], arn=res['thingTypeArn'], id=res['thingTypeId']))

def create_thing():
    thing_type = get_verified_env('BAKERHOUSE_IOT_THING_TYPE')
    thing_name = get_verified_env('BAKERHOUSE_IOT_THING')
    client=boto3.client('iot')

    print("\nTHING")

    res = client.list_things(thingTypeName=thing_type)
    #print("list_things:", res)
    
    for thing in res['things']:
        if thing['thingName'] == thing_name:
            print("{} already exists.".format(thing_name))
    else:
        res = client.create_thing(
                            thingName=thing_name,
                            thingTypeName=thing_type )
        #print("created, info:", res)

    res = client.describe_thing(thingName=thing_name)
    #print("describe_thing:", res)
    print("Name: {name}\nARN: {arn}\nID: {id}".format( name=res['thingName'], arn=res['thingArn'], id=res['thingId']))

    res = client.describe_endpoint()
    #print("describe_endpoint:", res)
    print("Endpoint address: {}".format(res['endpointAddress']))
    if get_verified_env('BAKERHOUSE_ENDPOINT', exit_on_fail=False) != res['endpointAddress']:
        print("WARNING: Environment variable BAKERHOUSE_ENDPOINT must be set to this value!")

def create_policy():
    """create AWS IoT policy for my thing"""
    client=boto3.client('iot')

    print("\nPOLICY")

    policy_name = get_verified_env('BAKERHOUSE_IOT_THING_POLICY')

    policy_found = False

    res = client.list_policies()
    #print("policies:", res)
    for policy in res['policies']:
        if policy['policyName'] == policy_name:
            print("Policy {} already exists.".format(policy_name))
            policy_found = True
            break

    if not policy_found:
        policy_document = '{"Version": "2012-10-17", "Statement": [ {  "Effect": "Allow", "Action": "iot:*", "Resource": "*" } ]}'
        res = client.create_policy(policyName=policy_name, policyDocument=policy_document)
        #print("created policy:", res)

    res = client.get_policy(policyName=policy_name)
    #print("policy:", res)
    print("Policy: {name}\nARN: {arn}".format(name=policy_name, arn=res['policyArn']))

def create_certificate_and_keys():
    client=boto3.client('iot')

    print("\nKEYS AND CERTS")

    cert_file=get_verified_env('BAKERHOUSE_MYCERT_FILE')
    privatekey_file=get_verified_env('BAKERHOUSE_PRIVATEKEY_FILE')
    publickey_file=get_verified_env('BAKERHOUSE_PUBLICKEY_FILE')
    root_cert_file=get_verified_env('BAKERHOUSE_ROOTCERT_FILE')

    # save root certificate
    root_ca_url="https://www.symantec.com/content/en/us/enterprise/verisign/roots/VeriSign-Class%203-Public-Primary-Certification-Authority-G5.pem"
    res = requests.get(root_ca_url)
    if res.status_code == 200:
        os.makedirs(os.path.dirname(root_cert_file), exist_ok=True)
        with open(root_cert_file, "w") as f:
            f.write(res.text)
    print("root cert saved to:", root_cert_file)

    # Checking whether you have ANY certs set up, in which case we bail.
    # ZZZ: check 'certificatePem' for a match with the contents of cert_file
    res = client.list_certificates()
    #print("certificates", res['certificates'])
    if res['certificates']:
        print("certificates exist, assuming you're already set up")
        for cert in res['certificates']:
            print("\n\tARN:{}\n\tID: {}\n\tStatus: {}\n\tCreated: {}".format(cert['certificateArn'], cert['certificateId'], cert['status'], cert['creationDate']))
        return

    res = client.create_keys_and_certificate(setAsActive=True)
    print("certificate created. ARN:{}\nID: {}".format(res['certificateArn'], res['certificateId']))
    #print("certificate:", res)

    # save keys
    os.makedirs(os.path.dirname(cert_file), exist_ok=True)
    with open(cert_file, "w") as f:
        f.write(res['certificatePem'])

    os.makedirs(os.path.dirname(privatekey_file), exist_ok=True)
    with open(privatekey_file, "w") as f:
        f.write(res['keyPair']['PrivateKey'])

    os.makedirs(os.path.dirname(publickey_file), exist_ok=True)
    with open(publickey_file, "w") as f:
        f.write(res['keyPair']['PublicKey'])

    print("keys saved")

def attach_to_cert():
    print("\nATTACH")

if __name__ == "__main__":
    create_thing_type()
    create_thing()
    create_policy()
    create_certificate_and_keys()
    attach_to_cert()

