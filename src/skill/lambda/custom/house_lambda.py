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
from os import environ

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

def build_response(session_attributes, title, output, reprompt_text, should_end_session):

    session_debug_message = "ENDING SESSION" if should_end_session else "KEEPING SESSION OPEN"
    log.debug(session_debug_message)

    

    speechlet_response =  {
        'outputSpeech': { 'type': 'PlainText', 'text': output},
        'card': { 'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'shouldEndSession': should_end_session
    }

    if reprompt_text is not None:
        speechlet_response['reprompt'] =  { 'outputSpeech': { 'type': 'PlainText', 'text': reprompt_text } }

    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }



def numeric_slot_value(slot):
    if slot is not None:
        num_value = slot['value']
        if num_value != "?":
            return int(num_value)
    return None

def string_slot_value(slot):
    #log.debug("string_slot_value - slot: %s", slot)
    str_value = None
    if slot is not None:
        str_value = slot['value']
        log.debug("string_slot_value - slot: %s value: %s", slot['name'], slot['value'])
    else:
        log.debug("string_slot_value - slot is None")
    return str_value


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

general_prompt = "You can select and input source or change the volume."
input_select_prompt =  "You can select an input source by saying, select input sonos"
volume_level_prompt =  "You can select the volume level by saying, volume 40"

def welcome_intent(session_attributes):
    """ Called when the user launches the skill without specifying what they want.
    If we wanted to initialize the session to have some attributes we could
    add those here.
    """

    session_attributes['baker_is_open'] = True

    card_title = "Welcome"
    speech_output = "Hi."
    reprompt_text = general_prompt
    should_end_session = False

    return build_response(session_attributes, card_title, speech_output, reprompt_text, should_end_session)


def cancel_intent(session_attributes):
    card_title = "Session Ended"
    speech_output = "Bye."
    should_end_session = True

    return build_response({}, card_title, speech_output, None, should_end_session)


def keep_baker_open(session_attributes):
    return  session_attributes.get('baker_is_open', False)

def select_input(intent, session_attributes):
    """ select receiver input source """

    card_title = intent['name']
    should_end_session = not keep_baker_open(session_attributes)

    input_selection = None
    slot = intent_slot(intent, 'input_selection')
    input_selection = validated_slot_value(slot)

    if input_selection is not None:
        log.debug("inputs selection value: %s", input_selection)

        speech_output = "Setting input source to {}".format(input_selection)
        #reprompt_text = volume_level_prompt
        reprompt_text = ""

        # update the IoT device shadow
        payload = json.dumps( { 'state': { 'desired': {'input': input_selection}}} )

        client=boto3.client('iot-data')
        client.update_thing_shadow(thingName=thing_name, payload=payload)

    else:
        speech_output = "I didn't understand your selection. Please try again."
        reprompt_text = ""

    return build_response(session_attributes, card_title, speech_output, reprompt_text, should_end_session)


def power_control(intent, session_attributes):
    """change desired power state to on or off"""
    card_title = intent['name']
    should_end_session = not keep_baker_open(session_attributes)

    input_selection = None
    slot = intent_slot(intent, 'input_selection')
    input_selection = validated_slot_value(slot)

    if input_selection is not None:
        log.debug("inputs selection value: %s", input_selection)

        speech_output = "Setting input source to {}".format(input_selection)
        #reprompt_text = volume_level_prompt
        reprompt_text = ""

        # update the IoT device shadow
        payload = json.dumps( { 'state': { 'desired': {'input': input_selection}}} )

        client=boto3.client('iot-data')
        client.update_thing_shadow(thingName=thing_name, payload=payload)

    else:
        speech_output = "I didn't understand your selection. Please try again."
        reprompt_text = ""

    return build_response(session_attributes, card_title, speech_output, reprompt_text, should_end_session)


def power_control(intent, session_attributes):
    """change desired power state to on or off"""
    card_title = intent['name']
    should_end_session = not keep_baker_open(session_attributes)

    power_state = None
    slot = intent_slot(intent, 'power_state')
    power_state = validated_slot_value(slot)

    if power_state is not None:
        log.debug("power state: %s", power_state)

        speech_output = "Turning power {}".format(power_state)
        reprompt_text = ""

        # update the IoT device shadow
        payload = json.dumps( { 'state': { 'desired': {'power': power_state}}} )

        client=boto3.client('iot-data')
        client.update_thing_shadow(thingName=thing_name, payload=payload)


        if power_state == 'off':
            should_end_session = True

    else:
        speech_output = "I didn't understand your selection. Please try again."
        reprompt_text = ""

    return build_response(session_attributes, card_title, speech_output, reprompt_text, should_end_session)
    pass

def _get_volume_level():
    client=boto3.client('iot-data')
    response = client.get_thing_shadow(thingName=thing_name)
    streamingBody = response["payload"]
    shadow_state = json.loads(streamingBody.read())
    log.debug("shadow_state: %s", shadow_state)

    return int(shadow_state['state']['reported']['volume'])

def query_volume(intent, session_attributes):
    """query current volume from the thing shadow, and set an adjusted level"""
    card_title = intent['name']
    should_end_session = not keep_baker_open(session_attributes)

    current_volume_level = _get_volume_level()
    speech_output = "The volume level is {}".format(current_volume_level)
    should_end_session = not keep_baker_open(session_attributes)

    power_state = None
    slot = intent_slot(intent, 'power_state')
    power_state = validated_slot_value(slot)

    if power_state is not None:
        log.debug("power state: %s", power_state)

        speech_output = "Turning power {}".format(power_state)
        reprompt_text = ""

        # update the IoT device shadow
        payload = json.dumps( { 'state': { 'desired': {'power': power_state}}} )

        client=boto3.client('iot-data')
        client.update_thing_shadow(thingName=thing_name, payload=payload)


        if power_state == 'off':
            should_end_session = True

    else:
        speech_output = "I didn't understand your selection. Please try again."
        reprompt_text = ""

    return build_response(session_attributes, card_title, speech_output, reprompt_text, should_end_session)
    pass

def _get_volume_level():
    client=boto3.client('iot-data')
    response = client.get_thing_shadow(thingName=thing_name)
    streamingBody = response["payload"]
    shadow_state = json.loads(streamingBody.read())
    log.debug("shadow_state: %s", shadow_state)

    return int(shadow_state['state']['reported']['volume'])

def query_volume(intent, session_attributes):
    """query current volume from the thing shadow, and set an adjusted level"""
    card_title = intent['name']
    should_end_session = not keep_baker_open(session_attributes)

    current_volume_level = _get_volume_level()
    speech_output = "The volume level is {}".format(current_volume_level)
    reprompt_text = ""
    return build_response(session_attributes, card_title, speech_output, reprompt_text, should_end_session)


def relative_volume(intent, session_attributes):
    """query current volume from the thing shadow, and set an adjusted level"""
    card_title = intent['name']
    should_end_session = not keep_baker_open(session_attributes)

    current_volume_level = _get_volume_level()

    # change by how much?
    volume_change_slot = intent_slot(intent, 'volume_level_change')
    if volume_change_slot is None:
        volume_change = 10  # TODO: allow sticky override of hardcoded default
    else:
        volume_change = numeric_slot_value(volume_change_slot)

    # raise or lower volume?
    raise_lower_slot = intent_slot(intent, 'raise_lower')
    if raise_lower_slot is None:
        return build_response(session_attributes, card_title, "Hm.", None, should_end_session)
    rl_val = string_slot_value(raise_lower_slot)

    log.debug("rl_val: %s", rl_val)
    if rl_val == 'lower':
        volume_change = -volume_change

    # set volume level
    volume_level = current_volume_level+volume_change

    payload = json.dumps( { 'state': { 'desired': {'volume': volume_level}}} )
    client=boto3.client('iot-data')
    client.update_thing_shadow(thingName=thing_name, payload=payload)

    speech_output = "Changing volume level by {}, to {}".format(volume_change, volume_level)
    reprompt_text =""
    return build_response(session_attributes, card_title, speech_output, reprompt_text, should_end_session)

def set_volume(intent, session_attributes):
    """ set receiver volume (may be capped). """

    card_title = intent['name']
    should_end_session = not keep_baker_open(session_attributes)

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
        #reprompt_text = input_select_prompt
        reprompt_text = ""
    else:
        speech_output = "I didn't understand your selection. Please try again." + volume_level_prompt
        #reprompt_text = "I didn't understand your selection." + volume_level_prompt
        reprompt_text = ""

    return build_response(session_attributes, card_title, speech_output, reprompt_text, should_end_session)


# --------------- EVENTS ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    log.debug("on_session_started requestId=%s sessionId=%s", session_started_request['requestId'], session['sessionId'])


def on_launch(launch_request, session_attributes):
    """ Called when the user launches the skill without specifying what they want """

    log.debug("on_launch requestId= %s", launch_request['requestId'])
    return welcome_intent(session_attributes)


def on_intent(intent_request, session_attributes):
    """ Called when the user specifies an intent for this skill """

    log.info("on_intent requestId=%s", intent_request['requestId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']
    log.info("intent name: %s", intent_name)

    # Dispatch to your skill's intent handlers
    if intent_name == "set_volume":
        return set_volume(intent, session_attributes)
    elif intent_name == "select_input":
        return select_input(intent, session_attributes)
    elif intent_name == "query_volume":
        return query_volume(intent, session_attributes)
    elif intent_name == "relative_volume":
        return relative_volume(intent, session_attributes)
    elif intent_name == "power_control":
        return power_control(intent, session_attributes)

    elif intent_name == "AMAZON.HelpIntent":
        return welcome_intent(session_attributes)
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return cancel_intent(session_attributes)
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
    log.debug("LAMBDA_HANDLER: event: %s", event)
    log.debug("lambda_handler: event.session.application.applicationId=%s", event['session']['application']['applicationId'])


    session_attributes = event['session'].get('attributes', {})
    log.debug("keep_baker_open %s", keep_baker_open(session_attributes))

    global thing_name
    thing_name = environ.get('BAKERHOUSE_IOT_THING')
    if thing_name is None:
        log.error("lambda_handler: required environment variable 'BAKERHOUSE_IOT_THING' is not set")
        return

    """
    Uncomment this block and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """

    log.info("invoking applicationId: %s", event['session']['application']['applicationId'])
    skill_app_id = "amzn1.echo-sdk-ams.app.[unique-value-here]"
    # ZZZ: will need to configure this from the environment config

    perform_app_id_check = False
    if  perform_app_id_check:
        if (event['session']['application']['applicationId'] !=
                "amzn1.echo-sdk-ams.app.[unique-value-here]"):
            raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']}, event['session'])

    log.debug("TYPE: %s", event['request']['type'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], session_attributes)
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], session_attributes)
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])

