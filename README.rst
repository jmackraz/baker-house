=======================
Baker House Project
=======================

Introduction
------------

This is a home automation hobby project, to control whatever you want
on a Raspberry Pi (for example) by voice, using Alexa, AWS Lambda and AWS IoT, all
in Python.  In this implementation, we use the onkly-eiscp package to control
an Onkly/Integra AV Receiver.

It is a goal to make this as absolutely simple as possible.  At runtime, there
are only three Python files: a Lambda function in the cloud, the client side of an AWS IoT
connection, and a simple server that provides a REST API to control the AV Receiver.

Apart from a stripped-down Pyramid application for the REST service, there
aren't any home automation or other frameworks.  Configuration is managed by a
environment variables exported from a setup file.

While the code is very simple, setting up everything necessary in AWS/Alexa is
not.  Tutorials walk us through a lot of clicking in consoles, creating
entities, downloading certificates and keys, selecting configurations, and
associating or attaching them correctly.

In this project, all of this setup is now scripted and instant once you've set up your
AWS and Alexa Skills Kit (ASK) account and some of the tools.  The setup scripts 
are illustrative, particularly regarding the AWS IoT configuration.  The
Alexa skill and its Lambda are deployed from local files using the ASK CLI,
which also provides a productive development workflow for ongoing
development of the skill.

By it's nature, this skill isn't something you would publish as is. It's a
learning exercise and you can use the skill in your house to control your own stuff.

But it only works if you have an Echo device registered to the AWS developer
account to which you deployed the skill. If your home Echos are on a
separate, "consumer" account, you must either register one of the Echos to your AWS
account, or you can add AWS  to your consumer account and deploy the skill to that.

There's some more information on managing multiple AWS accounts TO BE PROVIDED,
as I had to sort this out for myself.

High Level Architecture
-----------------------

Here's a walk through the architecture, following what happens when you say, "Alexa, ask Baker House to set volume to 30."

Echo Device:
    Your words are sent to Alexa, associated with your account, and all the skills you have installed.
    Our skill (*Baker House*) is available if the Echo is registered to your AWS account.

Alexa Skill:
    Alexa identifies our skill by its *Invocation Phrase* ("Baker House").  It
    parses the speech according to our skill's *Interaction Model* and
    determines the *Intent* (set volume) and the value of the *numeric slot* (30).

    Alexa then passes all this in a call to our associated Lambda function.

Lamba Function:
    Our Lambda function object in the cloud comprises the code (a single Python file), the specification
    of a runtime (python3.6) and our code entry point or *handler*.

    It receives the intent and slots from Alexa and in turn it tells our AWS
    IoT *Thing* that the desired volume should be 30.

Thing:
    This entity in the AWS IoT service is the rendevous point where our cloud code (Lambda)
    and our client code meet.

    We use the Thing's *Device Shadow* model, that is, a shadow copy of the
    state of the home system (volume, input selection).  In this case, our
    Lambda specifies the (*desired*) state of the volume to be 30.

    When this happens, the Thing sends  *delta update message* to its connected *IoT Client*.

IoT Client:
    Back in your house, a Python program uses the AWS IoT Client API library
    *AWSIoTPythonSDK* to establish and maintain a **persistent** connection to
    the AWS IoT service.

    The client will receive the delta updates from the IoT device shadow. It processes these
    by making a request to the RESTful *Hub Service*.

Hub Service:
    This service provides a small API to control the AV receiver, based on the onkyo-eiscp package.

    This service also provides a method to query the AV Receiver for its state. The IoT Client polls this method
    and will relay any detected changes (made by a human using the remote control) back up to the IoT device shadow.


It's just that simple, except for one thing: Security.  There are a number of
very different policies and certificates involved at each step, not to mention
the AWS and ASK credentials you need to do development.  This is why the setup
scripts are so helpful.  A listing of the security aspects of the project are
TO BE PROVIDED.


To Do
-----

- support "Alexa ... what is the current volume/input selection?"
- refine the interaction model; it stays open and nags.
- finish documentatino


Installation
------------

Rewrite this:

- Development prerequisites: AWS/ASK, python3, venv/wrapper
- Project setup: ``pip install -r REQUIREMENTS.txt`` and create ``setup_environment.sh`` from the provided template
- Run ``scripts/config_aws_iot.py`` to create (or list) all the IoT setup
- ``cd src/skill`` and type ``ask deploy`` to create (later, to update) the skill and the lambda
- ``./post_deploy.py`` to tweak the lambda created above
- Run tests, start client and hub services

Configuration
-------------
Configuration is done via environment variables. The recommended practice:

#. Copy the file scripts/setup_environment_template.sh to the file setup_environment.sh
#. Confirm that it is ignored by git, that is, it won't be checked in ever
#. Fill the values with your configuration secrets
#. Add these values to your environment::

     source setup_environment.sh

For details on the AWS / Alexa configuration and instant set up, see `Cloud Config`_

.. _`Cloud Config`: https:docs/house_config.rst


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
  Small RESTful service based on Pyramid and Cornice. It uses onkyo-eiscp python package to control Onkyo/Integra receivers.

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

