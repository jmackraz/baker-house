=======================
Baker House Project
=======================

Status
------

Doesn't work yet.

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

The hub service (in the ./hub directory) is a pyramid app (because I'm familiar) and you have to install it as per Pyramid cookiecutter instructions.  Specfically:

#. Create a virtualenv
#. Within that env, cd to hub and invoke::

    pip install -e .
#. Start the waitress server with auto-reload of edited python files::

    pserver --reload hub.ini

Configuration
-------------
Configuration is done via environment variables.  The recommended practice:

#. Copy setup_environment_template.sh to setup_environment.sh
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

update_lambda.sh
  Shell script that updates the local copy of house_lambda.py into the cloud Lambda,
  by creating a zip file and uploading it using the AWS CLI.

house_iot.py
  This runs in the house, and connects as a client to AWS IoT. It receives 
  home audio and other state changes via the device shadow. It is built from an example 
  and takes key/cert/endpoint parameters via the command line

  It interacts with the audio and other devices in the house by the 'hub' service REST API.

start_iot.sh
  Small shell script to start house_iot.py, passing paramters from the configuration environment variables.

hub/
  Small RESTful service based on Pyramid and Cornice.  It uses <name here> python package to control Onkyo/Integra receivers.

setup_environment_template.sh
  Template for setting up your configuration parameters/secrets as per the `Configuration`_ section above.
