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


class IoTConfig:

    def __init__(self):
        self.iot = boto3.client('iot')
        self.thing_name = get_verified_env('BAKERHOUSE_IOT_THING')
        self.thing_type = get_verified_env('BAKERHOUSE_IOT_THING_TYPE')
        self.policy_name = get_verified_env('BAKERHOUSE_IOT_THING_POLICY')
        self.cert_file=get_verified_env('BAKERHOUSE_MYCERT_FILE')
        self.privatekey_file=get_verified_env('BAKERHOUSE_PRIVATEKEY_FILE')
        self.publickey_file=get_verified_env('BAKERHOUSE_PUBLICKEY_FILE')
        self.root_cert_file=get_verified_env('BAKERHOUSE_ROOTCERT_FILE')
        self.certificateArn=None

    def create_thing_type(self):
        print("\nTHING TYPE")

        # check if it exists
        res = self.iot.list_thing_types(thingTypeName=self.thing_type)
        # should contain only our thing type, if it exists
        if res['thingTypes']:
            print("{} already exists".format(self.thing_type))
            #print("thing:", res['thingTypes'][0])
        else:
            res = self.iot.create_thing_type(
                        thingTypeName=self.thing_type,
                        thingTypeProperties={'thingTypeDescription': "My Baker House IoT Thing Type"} )
            #print("created, info:", res)

        res = self.iot.describe_thing_type(thingTypeName=self.thing_type)
        #print("thing type:", res)
        print("Name: {name}\nARN: {arn}\nID: {id}".format( name=res['thingTypeName'], arn=res['thingTypeArn'], id=res['thingTypeId']))

    def create_thing(self):
        print("\nTHING")

        res = self.iot.list_things(thingTypeName=self.thing_type)
        #print("list_things:", res)
        
        for thing in res['things']:
            if thing['thingName'] == self.thing_name:
                print("{} already exists.".format(self.thing_name))
        else:
            res = self.iot.create_thing(
                                thingName=self.thing_name,
                                thingTypeName=self.thing_type )
            #print("created, info:", res)

        res = self.iot.describe_thing(thingName=self.thing_name)
        #print("describe_thing:", res)
        print("Name: {name}\nARN: {arn}\nID: {id}".format( name=res['thingName'], arn=res['thingArn'], id=res['thingId']))

        res = self.iot.describe_endpoint()
        #print("describe_endpoint:", res)
        print("Endpoint address: {}".format(res['endpointAddress']))
        if get_verified_env('BAKERHOUSE_ENDPOINT', exit_on_fail=False) != res['endpointAddress']:
            print("WARNING: Environment variable BAKERHOUSE_ENDPOINT must be set to this value at runtime!")

    def create_policy(self):
        """create AWS IoT policy for my thing"""
        print("\nPOLICY")

        policy_found = False

        res = self.iot.list_policies()
        #print("policies:", res)
        for policy in res['policies']:
            if policy['policyName'] == self.policy_name:
                print("Policy {} already exists.".format(self.policy_name))
                policy_found = True
                break

        if not policy_found:
            policy_document = '{"Version": "2012-10-17", "Statement": [ {  "Effect": "Allow", "Action": "iot:*", "Resource": "*" } ]}'
            res = self.iot.create_policy(policyName=self.policy_name, policyDocument=policy_document)
            #print("created policy:", res)

        res = self.iot.get_policy(policyName=self.policy_name)
        #print("policy:", res)
        print("Policy: {name}\nARN: {arn}".format(name=self.policy_name, arn=res['policyArn']))

    def create_certificate_and_keys(self):
        print("\nKEYS AND CERTS")

        # save root certificate
        root_ca_url="https://www.symantec.com/content/en/us/enterprise/verisign/roots/VeriSign-Class%203-Public-Primary-Certification-Authority-G5.pem"
        res = requests.get(root_ca_url)
        if res.status_code == 200:
            os.makedirs(os.path.dirname(self.root_cert_file), exist_ok=True)
            with open(self.root_cert_file, "w") as f:
                f.write(res.text)
        print("root cert saved to:", self.root_cert_file)

        # Checking whether you have ANY certs set up, in which case we bail.
        res = self.iot.list_certificates()

        #### THIS IS NOT GOOD ENOUGH
        # for each certificate, determine if it has our Thing attached
        # If so, save the ARN, but don't create a new one.
        # If not, create and save the ARN

        if res['certificates']:
            print("certificates exist, checking whether you're already set up")
            for cert in res['certificates']:


                res = self.iot.list_principal_things(principal=cert['certificateArn'])
                #print("attached_things:", res)

                for thing in res['things']:
                    if thing == self.thing_name:
                        print
                        print("Found existing certificate attached to thing.\n\tARN:{}\n\tID: {}\n\tStatus: {}\n\tCreated: {}".format(
                            cert['certificateArn'], cert['certificateId'], cert['status'], cert['creationDate']))
                        self.certificateArn=cert['certificateArn']
                        return


        # no prior attached certificate found
        res = self.iot.create_keys_and_certificate(setAsActive=True)
        print("certificate created. ARN:{}\nID: {}".format(res['certificateArn'], res['certificateId']))

        # save the ARN for subsequent attach operations
        self.certificateArn=res['certificateArn']

        # save keys
        os.makedirs(os.path.dirname(self.cert_file), exist_ok=True)
        with open(self.cert_file, "w") as f:
            f.write(res['certificatePem'])

        os.makedirs(os.path.dirname(self.privatekey_file), exist_ok=True)
        with open(self.privatekey_file, "w") as f:
            f.write(res['keyPair']['PrivateKey'])

        os.makedirs(os.path.dirname(self.publickey_file), exist_ok=True)
        with open(self.publickey_file, "w") as f:
            f.write(res['keyPair']['PublicKey'])

        print("keys saved")

    def attach_to_cert(self):
        print("\nATTACH")

        if self.certificateArn is None:
            print("Certificate not found; skipping attachment operations")
            return

        # attach thing and policy to certificate, if not already done
        res = self.iot.list_principal_things(principal=self.certificateArn)
        if self.thing_name in res['things']:
            print("Thing {thing} already attached to certificate.".format(thing=self.thing_name))
        else:
            print("Attaching {thing} to certificate.".format(thing=self.thing_name))
            response = self.iot.attach_thing_principal( thingName=self.thing_name, principal=self.certificateArn)

        res = self.iot.list_attached_policies(target=self.certificateArn)
        #print("list_attached_policies result:", res)
        if self.policy_name in [policy['policyName'] for policy in res['policies']]:
            print("Policy {policy} already attached to certificate.".format(policy=self.policy_name))
        else:
            print("Attaching {policy} to certificate.".format(policy=self.policy_name))
            response = self.iot.attach_policy( policyName=self.policy_name, target=self.certificateArn)

    def build_all(self):
        self.create_thing_type()
        self.create_thing()
        self.create_policy()
        self.create_certificate_and_keys()
        self.attach_to_cert()

if __name__ == "__main__":
    iot_config = IoTConfig()
    iot_config.build_all()

