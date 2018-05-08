#!/usr/bin/env python
import os
from os import environ
import json
import boto3

# get skill's lambda name from deployment config file
# assume the skill name is the same for all profiles,
# and that AWS_PROFILE will be set (or not) to select
# the correct profile

# ZZZ- accept path to skill project from the command line
path_to_skill_project="."

path_to_deploy_config = os.path.join(path_to_skill_project, ".ask/config")


with open(path_to_deploy_config) as f:
    deploy_settings = json.load(f)['deploy_settings']

    #print("deploy_settings:", deploy_settings)

    # use first profile (python3 syntax)
    config = next (iter (deploy_settings.values()))
    #print("config:", config)

    lambda_name = config["merge"]["manifest"]["apis"]["custom"]["endpoint"]["uri"]

print("updating configuration for:", lambda_name)

lambda_client = boto3.client('lambda')

runtime="python3.6"
handler="house_lambda.lambda_handler"

print("updating runtime to:", runtime, " handler:", handler)
lambda_client.update_function_configuration(FunctionName=lambda_name, Runtime=runtime, Handler=handler)

thing_name = environ.get('BAKERHOUSE_IOT_THING')

print("setting lambda environment variable 'BAKERHOUSE_IOT_THING' to:", thing_name)
lambda_client.update_function_configuration(FunctionName=lambda_name, Environment={'Variables':{'BAKERHOUSE_IOT_THING':  thing_name}})


