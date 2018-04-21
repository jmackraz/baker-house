=======================
Baker House Project
=======================

Introduction
------------

This is a home automation hobby project. The goal
is to be able to execute any commands I want on a Raspberry Pi 
in my house, using Alexa. There are no home automation frameworks, pluggable interfaces, controllable device adapters/drivers. Just Python. Development can be done entirely on my Macbook, using the python AWS IoT API.

Architecture:
    Alexa Skill -> Lambda -> AWS IoT (device shadow) -> HOUSE FIREWALL -> IoT Python Client -> home control hub RESTful service

There is a lot of Alexa and IoT setup that is not yet documented here.


Status
------

* IT WORKS!

To Do
-----

V1

- DONE Wire up the library for controlling actual receiver
- DONE Aliases: sonos<->cd, directv<->sat
- DONE Figure out whether to reconcile one-to-many and sonos mapping in return values
- DONE Confirm update of values from hardware work for IoT

V2

- support "Alexa ... what is the current input selection?"
- Current requires an Echo registered to my AWS account. Explore options.
- handle ValueError exceptions for bad input

Later

- Write up minimalist instructions for how to set up the AWS stuff
- Explore using a repository for skill configuration/interaction, with or without lambda [any secrets in there?]
- Maybe some scripts that set up all the AWS stuff, based on config values you specify
- Maybe one solution will be to set up everything from recipe in an AWS account tied to my consumer login.


Installation
------------

#. Check out this repository
#. (Within a virtual env) install dependencies::

    pip install -r REQUIREMENTS.txt


Configuration
-------------
Configuration is done via environment variables. The recommended practice:

#. Copy the file scripts/setup_environment_template.sh to the file setup_environment.sh
#. Confirm that it is ignored by git, that is, it won't be checked in ever
#. Fill the values with your configuration secrets
#. Add these values to your environment::

     source setup_environment.sh

What's Here
-----------

house_lambda.py
  Implementation of an Alexa skill. It communicates
  with the device in my home via the AWS IoT APIs,
  by updating the device shadow corresponding to my home hub state.

  **STATUS:** Working.  Need to add queries against device shadow ("What is the current volume?")

update_lambda.sh
  Shell script that updates the local copy of house_lambda.py into the cloud Lambda,
  by creating a zip file and uploading it using the AWS CLI.

  **STATUS:** Working. (May try ASK update approach)

house_iot.py
  This runs in the house, and connects as a client to AWS IoT. It receives 
  home audio and other state changes via the device shadow. It is built from an example 
  and takes key/cert/endpoint parameters via the command line

  It interacts with the audio and other devices in the house by the house_hub service REST API.

  Start the client by executing this file as a script.

  **STATUS:** Working, including integration with house_hub

house_hub.py
  Small RESTful service based on Pyramid and Cornice. It uses <name here> python package to control Onkyo/Integra receivers.

  Start the service (currently hardcoded to waitress) by executing this file as a script.
  As an alternative, if you want the magical restat of the app when you modify a source file, you can also start the service using pserve,
  and a simple paste.deploy config file, as follows, from the root dir;

    env PYTHONPATH="src" pserve --reload house_hub_paste.ini


  **STATUS:** Working, including aliases (e.g., "directv" <-> "sat")
  Simplifed some more by stripping out unecessary base class
  Need to handle ValueError exceptions from bogus input values

setup_environment_template.sh
  Template for setting up your configuration parameters/secrets as per the `Configuration`_ section above.

scripts/
    Various scripts for making test REST requests against the hub service, poking the IoT device shadow, etc.

Resources
---------

Prequisites

* AWS Developer Signup
* AWS IoT Servcice: Console, Documentation
* Alexa Skill Developer Sign-up
* Alexa Skill (new) Console

Project

* AWS General: CLI, Python binding - boto3
* AWS IoT Python Library: Intro, API
* REST Service: Pyramid, Cornice, Colander, Cornice_Swagger
* Standard Python: requests, json, logging
* Alexa Skill Kit CLI (requires Node.js)

