=======================
Baker House Project
=======================

Introduction
============

This is a home automation hobby project, to control whatever you want to control on
a Raspberry Pi (for example) by voice, using Alexa, AWS Lambda and AWS IoT, all
in Python.  In this implementation, we use the onkyo-eiscp package to control
an Onkly/Integra AV Receiver.

It is a goal to make this as absolutely simple as possible.  At runtime, there
are only three Python files: a Lambda function in the cloud, the client side of an AWS IoT
connection, and a simple server that provides a REST API to control the AV Receiver.

Apart from a stripped-down Pyramid application for the REST service, there
aren't any home automation or other frameworks.  Configuration is managed by
environment variables exported from a setup file.

While the code is very simple, setting up everything necessary in AWS/Alexa is
not.  AWS and Alexa tutorials walk us through a lot of clicking in consoles, creating
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

But that only works if you have an Echo device registered to the AWS developer
account under which you deployed the skill. If your home Echos are on a
separate, "consumer" account, you must either register one of the Echos to your AWS
account, or you can add AWS to your consumer account and deploy the skill to that "profile."

I took the path of developing under my AWS developer login, then re-deploying
the work under my consumer account for use with my home Echos. Therefore the
setup scripts work with multiple AWS and Alexa Skills Kit logins (or
"profiles").

High Level Architecture
=======================

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

    When this happens, the Thing sends a *delta update message* to its connected *IoT Client*.

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
scripts are so helpful.  

What's Here
===========

house_lambda.py
  Implementation of an Alexa skill. It communicates
  with the device in my home via the AWS IoT APIs,
  by updating the device shadow corresponding to my home hub state.

  This file is found under the src/skill directory.  It is most conveniently updated
  to the cloud using the ``ask deploy`` command.

house_iot.py
  This runs in the house, and connects as a client to AWS IoT. It receives 
  home audio and other state changes via the device shadow. It is built from an example 
  and takes key/cert/endpoint parameters via the command line

  It interacts with the audio and other devices in the house by the house_hub service REST API.

  Start the client by executing this file as a script.

house_hub.py
  Small RESTful service based on Pyramid and Cornice. It uses onkyo-eiscp python package to control Onkyo/Integra receivers.

  Start the service (currently hardcoded to waitress) by executing this file as a script.

  As an alternative, if you want the magical restat of the app when you modify a source file, you can also start the service using ``pserve``,
  and a simple paste.deploy config file, as follows, from the top level directory;

    env PYTHONPATH="src" pserve --reload house_hub_paste.ini

setup_environment_template.sh
    Template for setting up your configuration parameters/secrets as per the `Project Configuration`_ section above.

src/skill/
    Alexa Skill "local project" including skills properties and the voice UI
    interaction model.  The corresponding lambda function (house_lambda.py) is
    also under this directory.  

scripts/
    Various scripts for creating the AWS cloud entities and testing the various components.


To Do
=====

- refine the interaction model; the session stays open and nags.
- add incremental/relative volume command
- add receiver power control
- support "Alexa ... what is the current volume/input selection?"
- recognize "direct tv" not just "directuhvuh"


Installation and Configuration
==============================

Development Prerequisites
-------------------------

Here are requirements and recommendations to set up before you get started.

Python 3:
    If you use a Mac, I recommend using Homebrew (https://brew.sh/) to augment your development environment, including the installation of Python 3.

Virtualenv/Virtualenvwrapper:
    Using some sort of "virtual environment" with Python allows you to use
    separate Python runtime and library package environments for each of your
    projects.

    I use virtualenv (https://virtualenv.pypa.io/en/stable/) and the very
    convenient helper package virtualenvwrapper (https://pypi.org/project/virtualenvwrapper/).
            
AWS Account:
    AWS Accounts are Amazon.com logins that are extended for AWS use by visiting https://aws.amzon.com.
    
    Note: Alexa skills not intended for publication, like this one, are available on Echo devices registered to the AWS account
    in which you set them up.  If you use an AWS account that is different than your normal home shopping and Alexa/Echo account,
    you'll need to dedicate an Echo device to that account, to test and use the skill.

    AWS tools allows you to manage more than one AWS account (or "Profile") and this project's configuration let's you select one,
    and keeps certificates and keys sorted out among multiple accounts.

    Learn about AWS enough to set up a secondary working login, rather than using your master account, and also set up 2-factor authentication.

AWS CLI:
    Install the AWS CLI to script and interactively explore or change anything in AWS (https://aws.amazon.com/cli/).

Alexa Skills Kit account and CLI:
    Visit https://developer.amazon.com/alexa-skills-kit and sign in to
    establish an Alexa development account.  Install the ASK CLI (it uses
    Node.js, which you can install using Homebrew (``brew install node``). It
    provides very useful commands for setting up and developing Alexa skills.

Project Configuration
---------------------

Once you clone this repository and set up and activate a virtualenv using python3, you can set up your configuration and start building the project.


Install Python Package Dependencies;
    This project does not include an installer.  To set up the necessary Python packages:

    ``pip install -r REQUIREMENTS.txt``

Customize Your Configuration:
    #. Copy the file ``scripts/setup_environment_template.sh`` to a file named ``setup_environment.sh`` in the top-level directory.
    #. Confirm that it is ignored by git, that is, that it won't be checked in, ever.
    #. Customize your settings by changing the values of variables in ``setup_environment.sh``.  If you have one an only one AWS/ASK account setup, the default values in this file are probably fine. Otherwise set appropriate values for the variables ``AWS_PROFILE`` and ``ASK_DEFAULT_PROFILE`` (these are the variables the CLIs use, and they are not named consistently). 
    #. Add these values to your environment::

         source setup_environment.sh

    If you use virtualenvwrapper 'mkproject' to set up an environment and working directory, this can be a useful
    way to set up your 'postactivate' script::

        #!/bin/bash
        # This hook is sourced after every virtualenv is activated.

        FILE=setup_environment.sh
        if [ -f $FILE ]; then
           echo "sourcing environment from $FILE"
           source $FILE
        fi


AWS Cloud Setup
===============
There are a number of AWS entities to be set up, as described in the section `High Level Architecture`_ above,
including an IoT Thing, Certificates, key pairs, policies, a
Lambda function called when your voice skill is invoked, and the Alexa Skill
itself, and various roles and other metadata.


AWS IoT Setup
-------------

To set up all the IoT entities, run this script from the top level project directory, with your environment set up::

    scripts/configure_aws_iot.py

This script will print progress while it's setting stuff up. If you run it again, it won't do any more setup, but it will print out
the details of your IoT setup for your review.

You may wish to go to the AWS IoT console and interactively explore the resulting Thing, Certificate, Policy and their relationships. (https://console.aws.amazon.com/iot/home).

Note that the setup script prints an AWS "endpoint" that will be needed at run time.  You should copy it to set the value of ``BAKERHOUSE_ENDPOINT`` in your ``setup_environment.sh`` file.  See comments in the file if you want to work with more than one AWS account profile and have separate endpoints for each.


Alexa Skill and Lambda Function Setup
-------------------------------------

The convenient way to setup and iterate development of an Alexa skill and its Lambda function is by using a "local project image" and the ASK CLI ``deploy`` command. For initial setup, run these commands::

    cd src/skill        # this is the root of the local skill project
    ask deploy          # the ASK CLI will set up the skill, Lambda, and everything else
    ./post_deploy.py    # This script will fix up the created skill and Lambda 

Later, as you edit your skill's voice interaction model, or the Lambda function, you invoke ``ask deploy`` again from that same directory, but you do not have to run ``post_deploy.py`` again.

You can see the results of this configuration in the Alexa console (https://developer.amazon.com/alexa/console/ask) and in AWS Lambda (https://aws.amazon.com/lambda/).

Startup and Testing
===================
Let's turn everything on and test it. 

#. The ``house_hub`` RESTful service and control of Onkyo/Integra AV receiver
#. The AWS IoT "Thing" set up in isolation
#. Connection from the AWS IoT Thing to our IoT client ``house_it`` and through to the ``house_hub`` service
#. Direct scripted invocation of our Lambda function ``house_lambda``. [I don't have this yet, because I haven't figured out how to simulate the context and parameters passed to the Lambda by a call from Alexa.]
#. Scripted test of our Alexa skill calling our Lambda and then all the way down to the ``house_hub``.
#. End-to-end Voice control.

All scripted tests run from the top-level project directory, after setting up the environment by executing ``source setup_environment.sh``.

Starting and Testing the ``house_hub`` RESTful Service
------------------------------------------------------

In one terminal window, start the service.  There are two options.  The simplest is to just run the script::

    src/house_hub.py

The network port and logging configuration is defined in the script source. I
use this method for "production," so log level is set to INFO.

The other approach is to use the paste.deploy configuration file
``house_hub_paste.ini`` and the Pyramid command ``pserve``.  This is good for
development because it gives the option to have the server restart
automatically every time you modify the source code.  Like so::

    env PYTHONPATH="src" pserve --reload house_hub_paste.ini

With this method, the port and logging level are configured in the
house_paste.ini file, and I have the log level set to DEBUG.

Choose a method and start the server.

Test the server using the command::

    src/test_home_hub.py

If you have an Onkyo or Integra AV receiver connected to the same network as your
development computer, you should see the receiver input switch to 'CD' but be
reported as 'sonos' because I have my Sonos node plugged into the CD input
jack.  It will also turn the volume to level 20 (low).

You can stop the server by typing Control-C in the terminal window.

AWS IoT Thing Configuration
---------------------------
    
Before we start our local IoT daemon, we test the IoT configuration with a simple standalone script::

    scripts/test_iot.py

This script connects to AWS IoT and listens for changes to our Thing's "device
shadow."  Every few seconds, the script posts a change in volume level.  When
AWS IoT echoes that change to the device shadow with a "device shadow delta"
message, the message is printed.  AWS seems to "miss" some changes, but it
should always echo back the final value that was posted.

IoT Client house_iot.py
-----------------------

It's time to start the IoT client.  If the house_hub service is running, you
will see it logging the polling GET requests that the house_iot client makes.
The tests may control your Onkyo.  If house_hub is not running, you'll see
error messages from the house_iot daemon.

In one terminal window start the client:

    src/house_iot.py

Now we'll programmatically issue a change to the IoT Thing device shadow in the
cloud, and we should see the change received by our local house_iot client, and
passed along to house_hub.

In another window, run::

    scripts/poke_iot.py

That command should succeed in connecting to AWS IoT and changing the input value, and
you should see the change cascade down to the house_iot client, then to the house_hub 
service, and ultimate, to your Onkyo.  If all this works but your Onkyo isn't turning on 
or otherwise responding to commands, check out the eiscp README: https://github.com/miracle2k/onkyo-eiscp


Go For It
---------

With an Echo device that is registered to the same account used for your AWS development, speak::

    "Alexa, ask Baker House to select sonos."

This should turn your receiver on, if necessary, and select the "CD" input (into which I connected my Sonos node).

I have not successfully figured out the "session" concept. Alexa will nag you
to: "Set volume to 40" until you say "Stop" or it gives up and replies, "Thank
you."  Sorry; I'll work on that.

What Now?
=========

If you have an Onkyo or Integra receiver, you can enjoy voice control of input selection or volume.  You can follow and/or help 
add new commands and state queries by modifying the skill's interaction model and the implementation within house_hub.py.

If you don't have such a receiver, you can tear up house_hub.py to create a REST API for whatever else you can do in Python that you'd like to control using Alexa.
You will change the voice user interface by editing the local interaction model, ``src/skill/models/en-US.json`` or figuring out how to use the Alexa console editor on the web.

Deploying
=========

You may want to run the house_iot client and the house_hub service on some other computer, such as a Raspberry Pi.  The important part is this:

**The AWS IoT certificates and keys are copied to your deployment machine, but your AWS and ASK account credentials are not.**

#. Stop the house_iot client and house_hub service on your development box.
#. Set up python3 and virtualenv/helper on your Pi, as in `Development Prerequisites`_
#. Clone this git project on the Pi. You could probably copy just the src/ directory from your development machine, but I like to be able to hot fixes under git for hobby projects.
#. Do NOT set up AWS or ASK CLI or credentials on the Pi.  You cannot run the poke_iot.py test without those credentials, but other tests should work.
#. Set up the `Project Configuration`_ using the same setup_environment.sh file that you used on your development machine to configure and test.
#. With the virtualenv and environment variables set up, start house_hub and house_iot as described above.

The problem with starting the client and hub service in tty/ssh windows is that they will stop running when you disconnect. Rather than figure out how to run these services as daemons, I use the fantastic ``screen`` utility that is available (standard?) on Linux and Mac OS. https://www.gnu.org/software/screen/manual/screen.html and https://www.tecmint.com/screen-command-examples-to-manage-linux-terminals/.

Here is a quick sequence with minimal explanation.

#. Log into pi using ssh in a terminal (from your development machine).
#. Start a named screen session with a large scrollback buffer::

    screen -h 1000 -D -R baker-house

#. Create a second virtual window within the screen session: ``Ctrl-a w``
#. See that you can toggle between the windows. First run ``ls`` or something in one window,
   then type: ``Ctrl-a Ctrl-a`` a couple of times.  Type ``Ctrl-a "`` to see a
   pick-list of windows.
#. In each of the two screen windows, setup your environment and start the house_iot client in one and the house_hub server in the other.
#. Detach from the screen session: ``Ctrl-a d``
#. See that your screen session still exists: ``screen -ls``
#. Reattach to the screen session: ``screen -D -R baker-house``



Resources
=========

Alexa Skill Developer

*    General, Sign-up (https://developer.amazon.com/alexa-skills-kit)
*    Alexa Skill (new) Console (https://developer.amazon.com/alexa/console/ask)
*    Alexa Skill Kit CLI (requires Node.js) (https://developer.amazon.com/docs/smapi/ask-cli-command-reference.html)

AWS

*    General (https://aws.amazon.com/)
*    CLI (https://docs.aws.amazon.com/cli/latest/reference/)
*    Python binding - boto3 (http://boto3.readthedocs.io/en/latest/index.html)
*    AWS IoT Console (https://console.aws.amazon.com/iot/home)
*    AWS IoT Python Library: Intro, API (https://github.com/aws/aws-iot-device-sdk-python)

RESTful Service

*    Pyramid (https://docs.pylonsproject.org/projects/pyramid/en/latest/)
*    Cornice (REST) (https://cornice.readthedocs.io/en/latest/)
*    Colander (schema definition) (https://docs.pylonsproject.org/projects/colander/en/latest/)

Standard Python libraries

*    requests (http://docs.python-requests.org/en/master/)
*    JSON (https://docs.python.org/3/library/json.html)
*    logging (https://docs.python.org/3/library/logging.html)

Onkyo-eiscp (https://github.com/miracle2k/onkyo-eiscp)
