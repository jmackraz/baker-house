=======================
Baker House Project
=======================

Status
------

Doesn't work yet.  All the pieces but the real Alexa skill have been proven out.

Introduction
------------

This is a home automation hobby project. The goal
is to be able to execute any commands I want on a Raspberry Pi 
in my house, using Alexa.

There are no home automation frameworks, pluggable interfaces, controllable device adapters/drivers.  Just Python.

Development can be done entirely on my Macbook, using the python AWS IoT API.

Architecture:
Alexa Skill -> Lambda -> AWS IoT (device shadow) -> HOUSE FIREWALL -> IoT Python Client -> home control hub RESTful service


There is a lot of Alexa and IoT setup that is not yet documented here.

The hub service (in the ./hub directory) is a pyramid app but unlike the cookiecutter example, it's self-contained in a single file.

Installation
------------

#. Check out this repository
#. (Within a virtual env) install dependencies::

    pip install -r REQUIREMENTS.txt


Configuration
-------------
Configuration is done via environment variables.  The recommended practice:

#. Copy the file scripts/setup_environment_template.sh to the file scripts/setup_environment.sh
#. Confirm that it is ignored by git, that is, it won't be checked in ever
#. Fill the values with your configuration secrets
#. Add these values to your environment::

     source setup_environment.sh

What's Here
-----------

house_lambda.py
  Implementation of an Alexa skill.  It communicates
  with the device in my home via the AWS IoT APIs,
  by updating the device shadow corresponding to my home hub state.

  **STATUS:** It's just a demo lambda at this time that tries out AWS IoT 'publish'

update_lambda.sh
  Shell script that updates the local copy of house_lambda.py into the cloud Lambda,
  by creating a zip file and uploading it using the AWS CLI.

  **STATUS:** Working

house_iot.py
  This runs in the house, and connects as a client to AWS IoT. It receives 
  home audio and other state changes via the device shadow. It is built from an example 
  and takes key/cert/endpoint parameters via the command line

  It interacts with the audio and other devices in the house by the 'hub' service REST API.

  Start the client by executing this file as a script.

  **STATUS:** Simplified 'subscribe' client, stub for polling source of truth

house_hub.py
  Small RESTful service based on Pyramid and Cornice.  It uses <name here> python package to control Onkyo/Integra receivers.

  Start the service (currently hardcoded to waitress) by executing this file as a script.

  **STATUS:** Working as a service, with Colander schema validation.  Emits an OpenAPI 2.0 JSON definition (that's not very useful).
  Ready to plug in the first couple of calls to actually control my receiver.

setup_environment_template.sh
  Template for setting up your configuration parameters/secrets as per the `Configuration`_ section above.

  **STATUS:** Template for all configuration environment variables used at this time

