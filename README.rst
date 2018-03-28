=======================
Baker House Project
=======================

Introduction
============

This is a home automation hobby project. The goal
is to be able to execute any commands I want on a Raspberry Pi 
in my house, using Alexa.

There are no home automation frameworks, pluggable interfaces, controllable device adapters/drivers.  Just Python.

Development can be done entirely on my Macbook, using the python AWS IoT API.

Architecture:
Alexa Skill -> Lambda -> AWS IoT (device shadow) -> HOUSE FIREWALL -> IoT Python Client -> home control hub RESTful service


There is a lot of Alexa and IoT setup that is not yet documented here.

The hub service (in the ./hub directory) is a pyramid app (because I'm familiar) and you have to install it as per Pyramid cookiecutter instructions.  Specfically:
1. Create a virtualenv
2. Within that env, cd to hub and invoke: ``pip install -e .``
3. Start the waitress server with auto-reload of edited python files: ``pserver --reload hub.ini``

