#!/usr/bin/env python

"""
Based on Skills SDK example
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

from __future__ import print_function

import logging
import boto3
import json

from sys import stdout
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
formatter = logging.Formatter('%(levelname)s - %(message)s')
handler = logging.StreamHandler(stdout)
handler.setFormatter(formatter)

#logging.basicConfig(format=formatter)

log = logging.getLogger(__name__)
log.addHandler(handler)
log.setLevel(logging.DEBUG)


# IoT thing name needs to come from the environment (set up in handler main)
thing_name = 'NOT_SET'


# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': { 'type': 'PlainText', 'text': output },
        'card': { 'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': { 'outputSpeech': { 'type': 'PlainText', 'text': reprompt_text } },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


def numeric_slot_value(slot):
    if slot is not None:
        num_value = slot['value']
        if num_value != "?":
            return num_value
    return None


def validated_slot_value(slot):
    """return a value for a slot that's been validated."""   
    if slot is not None:
        for resolution in slot['resolutions']['resolutionsPerAuthority']:
            if 'values' in resolution:
                return resolution['values'][0]['value']['name']
    return None


def intent_slot(intent, slot_name):
    """return slot dict, avoid key errors"""
    if slot_name in intent['slots'] and 'value' in intent['slots'][slot_name]:
        return intent['slots'][slot_name]
    return None

# --------------- INTENTS ------------------

input_select_prompt =  "You can select an input source by saying, select input sonos"
volume_level_prompt =  "You can select the volume level by saying, volume 40"

def welcome_intent():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to the Baker House. " + input_select_prompt
    reprompt_text = input_select_prompt
    should_end_session = False

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def cancel_intent():
    card_title = "Session Ended"
    speech_output = "Thank you, good bye!"
    should_end_session = True

    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def select_input(intent, session):
    """ select receiver input source """

    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    input_selection = None
    slot = intent_slot(intent, 'input_selection')
    input_selection = validated_slot_value(slot)

    if input_selection is not None:
        log.debug("inputs selection value: %s", input_selection)

        speech_output = "Setting input source to {}".format(input_selection)
        reprompt_text = input_select_prompt

        # update the IoT device shadow
        payload = json.dumps( { 'state': { 'desired': {'input': input_selection}}} )

        client=boto3.client('iot-data')
        client.update_thing_shadow(thingName=thing_name, payload=payload)

    else:
        speech_output = "I didn't understand your selection. Please try again."
        reprompt_text = "I didn't understand your selection." + input_select_prompt

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))



def set_volume(intent, session):
    """ set receiver volume (may be capped). """

    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    # the value is "?" if it's given bogus input
    slot = intent_slot(intent, 'volume_level')
    volume_level = numeric_slot_value(slot)
    if volume_level is not None:
        log.debug("volume level slot value: %s", volume_level)
        
        # update the IoT device shadow
        payload = json.dumps( { 'state': { 'desired': {'volume': volume_level}}} )

        client=boto3.client('iot-data')
        client.update_thing_shadow(thingName=thing_name, payload=payload)

        speech_output = "Volume level set to {}".format(volume_level)
        reprompt_text = volume_level_prompt
    else:
        speech_output = "I didn't understand your selection. Please try again."
        reprompt_text = "I didn't understand your selection." + volume_level_prompt

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


# --------------- EVENTS ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    log.debug("on_session_started requestId=%s sessionId=%s", session_started_request['requestId'], session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they want """

    log.debug("on_launch requestId= %s, sessionId=%s", launch_request['requestId'], session['sessionId'])
    # Dispatch to your skill's launch
    return welcome_intent()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    log.info("on_intent requestId=%s sessionId=%s", intent_request['requestId'], session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']
    log.info("intent name: %s", intent_name)

    # Dispatch to your skill's intent handlers
    if intent_name == "set_volume":
        return set_volume(intent, session)
    elif intent_name == "select_input":
        return select_input(intent, session)

    elif intent_name == "AMAZON.HelpIntent":
        return welcome_intent()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return cancel_intent()
    else:
        log.error("UNKNOWN INTENT: %s", intent_name)
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    log.info("on_session_ended requestId=" + session_ended_request['requestId'] + ", sessionId=" + session['sessionId'])


# --------------- Main handler ------------------

def lambda_handler(event, context):
    log.debug("lambda_handler: event: %s", event)
    log.debug("lambda_handler: event.session.application.applicationId=%s", event['session']['application']['applicationId'])

    global thing_name
    thing_name = environ.get('BAKERHOUSE_IOT_THING')
    if thing_name is None:
        log.error("lambda_handler: required environment variable 'BAKERHOUSE_IOT_THING' is not set")
        return

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    log.debug("TYPE: %s", event['request']['type'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])

