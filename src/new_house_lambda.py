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

from sys import stdout
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
formatter = logging.Formatter('%(levelname)s - %(message)s')
handler = logging.StreamHandler(stdout)
handler.setFormatter(formatter)

#logging.basicConfig(format=formatter)


log = logging.getLogger(__name__)
log.addHandler(handler)
log.setLevel(logging.DEBUG)



# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

input_select_prompt =  "You can select an input source by saying, select input sonos"

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



def test_intent(intent, session):
    """ play. """

    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    if 'InputSource' in intent['slots']:
        input_source = intent['slots']['InputSource']['value']
        speech_output = "Selecting {} for input".format(input_source)
        reprompt_text = input_select_prompt
    else:
        speech_output = "I didn't understand your selection. Please try again."
        reprompt_text = "I didn't understand your selection." + input_select_prompt

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


# --------------- Events ------------------

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
    if intent_name == "TestIntent":
        return test_intent(intent, session)

    elif intent_name == "AMAZON.HelpIntent":
        return welcome_intent()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return cancel_intent()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    log.info("on_session_ended requestId=" + session_ended_request['requestId'] + ", sessionId=" + session['sessionId'])


# --------------- Main handler ------------------

def lambda_handler(event, context):
    log.debug("lambda_handler: event.session.application.applicationId=%s", event['session']['application']['applicationId'])

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

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


if __name__=='__main__':

    new_session_event = {
        'session': {'new': True, 'application': {'applicationId': 'DUMMYID'}, 'sessionId': 'DUMMY_SESSION_ID'}, 
        'request': {'type': 'BLAH', 'requestId': 'BLAH'}
        }

    launch_event = {
        'session': {'new': False, 'application': {'applicationId': 'DUMMYID'}, 'sessionId': 'DUMMY_SESSION_ID'}, 
        'request': {'type': 'LaunchRequest', 'requestId': 'BLAH'}
        }

    intent_event = {
        'session': {'new': False, 'application': {'applicationId': 'DUMMYID'}, 'sessionId': 'DUMMY_SESSION_ID'}, 
        'request': {'type': 'IntentRequest', 'requestId': 'BLAH', 'intent': {'name': 'TestIntent', 'slots': [] }}
        }

    end_session_event = {
        'session': {'new': False, 'application': {'applicationId': 'DUMMYID'}, 'sessionId': 'DUMMY_SESSION_ID'}, 
        'request': {'type': 'SessionEndedRequest', 'requestId': 'BLAH'}
        }

    test_events = [ new_session_event, launch_event, intent_event, end_session_event ]
    #test_events = [ new_session_event ]


    for event in test_events:
        log.debug("call lambda_handler with fake event: %s", event['request']['requestId'])
        response = lambda_handler( event, None )
        log.debug("response: %s", response)
