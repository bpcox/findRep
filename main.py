from __future__ import print_function
import sunlight
import config

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    if (event['session']['application']['applicationId'] !=
             config.applicationid):
         raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "FindByZip":
        return get_representatives(intent)
    #elif intent_name == "FindSenByZip":
    #elif intent_name == "FindRepByZip":
    #elif intent_name == "FindContactInfo":
    #elif intent_name == "FindParty":
    #elif intent_name == "FindTerm":
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.
    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here

# --------------- Functions that control the skill's behavior ------------------

def get_representatives(intent):
    print(int(intent['slots']['zip']['value']))
    card_title = intent['slots']['zip']['value']
    should_end_session = True
    session_attributes = {}

    congressmen = sunlight.congress.locate_legislators_by_zip(intent['slots']['zip']['value'])
	
    if congressmen:

        card_title = intent['slots']['zip']
        
        senators = list()
	reps = list()
        for congressman in congressmen:
			if congressman['chamber']=='senate':
				senators.append(congressman)
			else:
				reps.append(congressman)
				
	if len(senators) is 2:
			senators_string = "Your senators are " + senators[0]['first_name'] + ' ' + senators[0]['last_name'] + " and " + senators[1]['first_name'] + ' ' + senators[1]['last_name'] + '. '
	elif len(senators) is 0:
			senators_string = "You have no senators."
        else:
			senators_string = "Your zip code crosses state boundaries."
			
	if len(reps) is 1:
			reps_string = "Your representative is " + reps[0]['first_name'] + ' ' + reps[0]['last_name'] + '. '
	else:
			reps_string = "This zip code has more than one representative. "
        
        speech_output = reps_string + senators_string

    else:
        speech_output = "Sorry, that isn't a valid zip code. " \
                        "Please try again."
    
    reprompt_text = ""                      
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))



def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {} 
    card_title = "Welcome"
    speech_output = "Ask for the representative for your zip code."
    
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = None
    
    should_end_session = True
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


        
# --------------- Helpers that build all of the responses ----------------------


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
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