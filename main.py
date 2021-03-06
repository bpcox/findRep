from __future__ import print_function
import sunlight
import config
import json

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Check Application ID
    """
    if (event['session']['application']['applicationId'] !=
         config.applicationid):
         raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']}, event['session'])

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
    elif intent_name == "GetParty":
        return get_party(intent)
    elif intent_name == "GetTwitter":
        return get_twitter(intent)
    elif intent_name == "GetPhone":
        return get_phone(intent)
    elif intent_name == "GetOffice":
        return get_office(intent)
    elif intent_name == "FindState":
        return get_state(intent)
    elif intent_name == "GetTermEnd":
        return get_term_end(intent)
    elif intent_name == "AMAZON.HelpIntent":
        return get_help()
    elif intent_name == "AMAZON.StopIntent" or "AMAZON.CancelIntent":
        return end_session()
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
    is_null = check_null(intent,'zip')
    if is_null:
        print ("This is null")
        return is_null
        
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
            senators_string = "Your senators could be " + reps[0]['first_name'] + ' ' + reps[0]['last_name']
            for i in range(1,len(senators)):
                if i%2 == 1:
                    senators_string += ' and ' + senators[i]['first_name'] + '' + senators[i]['last_name'] + ' of ' + expandState(senators[i])
                else:
                    senators_string+= ' or ' + senators[i]['first_name'] + ' ' + senators[i]['last_name']
            senators_string+='.'
        if len(reps) is 1:
            reps_string = "Your representative is " + reps[0]['first_name'] + ' ' + reps[0]['last_name'] + '. '

        else:
            reps_string = "Your representative could be " + reps[0]['first_name'] + ' ' + reps[0]['last_name']
            for i in range(1,len(reps)):
                reps_string += ' or ' + reps[i]['first_name'] + ' ' + reps[i]['last_name']
        reps_string += '. '
        speech_output = reps_string + senators_string

    else:
        speech_output = "Sorry, no congressman is listed for that zip code. " \
                        "Please try again."
    
    reprompt_text = ""                      
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_party(intent):
    is_null = check_null(intent,'rep')
    if is_null:
        return is_null
    print(intent['slots']['rep']['value'])
    card_title = intent['slots']['rep']['value']
    should_end_session = True
    session_attributes = {}
    name = (intent['slots']['rep']['value']).lower()
    print (name)
    congressman = findRep(name, 'congressNames.json')
    
    if congressman:
        if congressman['party'] == 'R':
            party = ' Republican'
        elif congressman['party'] == 'D':
            party = ' Democrat'
        else:
            party = 'n Independent'
        fulltitle = expandTitle(congressman)
        speech_output = fulltitle + ' ' + congressman['last_name'] + ' is a' + party

    else:
        speech_output = "Sorry, I didn't understand that representative. " \
                        "Please try again."
        should_end_session = False
    
    reprompt_text = "Try asking a different question"                      
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_twitter(intent):
    is_null = check_null(intent,'rep')
    if is_null:
        return is_null
    print(intent['slots']['rep']['value'])
    card_title = intent['slots']['rep']['value']
    should_end_session = True
    session_attributes = {}
    name = (intent['slots']['rep']['value']).lower()
    
    congressman = findRep(name, 'congressNames.json')

    if congressman:
        speech_output = generateAttributeString(congressman,'twitter_id','twitter account')

    elif findDuplicate(name, 'duplicateNames.json'):
        speech_output = "The title " + name.replace("'s","") + " is shared by more than one Congressman. Be more specific."
    else:
        speech_output = "Sorry, I didn't understand that representative. " \
                        "What information do you want?"
        should_end_session = False
    
    reprompt_text = "Try asking a different question."                      
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_phone(intent):
    is_null = check_null(intent,'rep')
    if is_null:
        return is_null
    print(intent['slots']['rep']['value'])
    card_title = intent['slots']['rep']['value']
    should_end_session = True
    session_attributes = {}
    name = (intent['slots']['rep']['value']).lower()
    
    congressman = findRep(name, 'congressNames.json')

    if congressman:
        speech_output = generateAttributeString(congressman,'phone','phone number')
    elif findDuplicate(name, 'duplicateNames.json'):
        speech_output = "The title " + name.replace("'s","") + " is shared by more than one Congressman. Be more specific."

    else:
        speech_output = "Sorry, I didn't understand that representative. " \
                        "Please try again."
        should_end_session = False
            
    reprompt_text = "Try asking a different question."                      
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_office(intent):
    is_null = check_null(intent,'rep')
    if is_null:
        return is_null
    print(intent['slots']['rep']['value'])
    card_title = intent['slots']['rep']['value']
    should_end_session = True
    session_attributes = {}
    name = (intent['slots']['rep']['value']).lower()
    
    congressman = findRep(name, 'congressNames.json',address=True)

    if congressman:
        speech_output = generateAttributeString(congressman,'full_address','address')

    elif findDuplicate(name, 'duplicateNames.json'):
        speech_output = "The title " + name.replace("'s","") + " is shared by more than one Congressman. Be more specific."
        
    else:
        speech_output = "Sorry, I didn't understand that representative. " \
                        "Please try again."
        should_end_session = False
    reprompt_text = "Try asking a different question"                      
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
        
def get_state(intent):
    is_null = check_null(intent,'rep')
    if is_null:
        return is_null
    print(intent['slots']['rep']['value'])
    card_title = intent['slots']['rep']['value']
    should_end_session = True
    session_attributes = {}
    name = (intent['slots']['rep']['value']).lower()
    
    congressman = findRep(name, 'congressNames.json')

    if congressman:
        speech_output = generateAttributeString(congressman,'state','state',state=True)

    elif findDuplicate(name, 'duplicateNames.json'):
        speech_output = "The title " + name.replace("'s","") + " is shared by more than one Congressman. Be more specific."
    else:
        speech_output = "Sorry, I didn't understand that representative. " \
                        "What information do you want?"
        should_end_session = False
    
    reprompt_text = "Try asking a different question"                      
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
        
    
def get_term_end(intent):
    is_null = check_null(intent,'rep')
    if is_null:
        return is_null
    print(intent['slots']['rep']['value'])
    card_title = intent['slots']['rep']['value']
    should_end_session = True
    session_attributes = {}
    name = (intent['slots']['rep']['value']).lower()
    
    congressman = findRep(name, 'congressNames.json')

    if congressman:
        speech_output = generateAttributeString(congressman,'term_end','end of term')

    elif findDuplicate(name, 'duplicateNames.json'):
        speech_output = "The title " + name.replace("'s","") + " is shared by more than one Congressman. Be more specific."
    else:
        speech_output = "Sorry, I didn't understand that representative. " \
                        "What information do you want?"
        should_end_session = False
    
    reprompt_text = "Try asking a different question."                      
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
        
def end_session():
    return build_response({}, build_speechlet_response("","","",True))

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {} 
    card_title = "Welcome"
    speech_output = "Ask for information about any US Congressman"
    
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "You can ask who the congrssmen are for a zip code, or ask for a specific congressman's phone number or mailing address"
    
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_help():
    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Ask for the Congressmen for a zip code or ask for a specific Congressman's contact information"

    reprompt_text = "For instance, you can ask, What is Representative Smith's twitter"
    should_end_session = False

    return build_response(session_attributes, build_speechlet_response(card_title,speech_output, reprompt_text, should_end_session))

def findRep(name,nameJSON, address=False):
    name=name.replace("'s",'')
    with open(nameJSON,'r') as f:
        nameDict = json.load(f)
    if address:
        with open('addressDict.json','r') as g:
            addressDict = json.load(g)
    for k,v in nameDict.iteritems():
        if name in v:
            print("found")
            legislator = sunlight.congress.legislator(k,id_type='bioguide')
            if address:
                legislator['full_address'] = addressDict[k]
            return legislator
    return None

def findDuplicate(name,duplicateJSON):
    name=name.replace("'s",'')
    with open(duplicateJSON,'r') as f:
        duplicateDict = json.load(f)
    for k,v in duplicateDict.iteritems():
        if name in v:
            print("Duplicate found")
            return True
    return False

def generateAttributeString(rep,attribute,nickname,state=False):
    fulltitle = expandTitle(rep)
    if attribute in rep and rep[attribute] != None:
        resultAttribute = rep[attribute]
    else:
        return fulltitle + ' ' + rep['first_name'] + ' ' + rep['last_name'] + " does not have a " + nickname

    if state:
        resultString = "The " + nickname + " for " + fulltitle + ' ' + rep['first_name'] + ' ' + rep['last_name'] + \
        ' is ' + expandState(resultAttribute)
        return resultString
    resultString = "The " + nickname + " for " + fulltitle + ' ' + rep['first_name'] + ' ' + rep['last_name'] + \
    ' is ' + resultAttribute
    return resultString


def expandTitle(rep):

    titleDict =  {'Rep': 'Representative','Sen':'Senator','Com':'Commissioner','Del':'Delegate'}
    try:
        return titleDict[rep['title']]
    except KeyError:
        return ''
    
def expandState(rep):
    stateDict = {'AL':'Alabama',
    'AK':'Alaska',
    'AS':'American Samoa',
    'AZ':'Arizona',
    'AR':'Arkansas',
    'CA':'California',
    'CO':'Colorado',
    'CT':'Connecticut',
    'DE':'Delaware',
    'DC':'District of Columbia',
    'FL':'Florida',
    'GA':'Georgia',
    'GU':'Guam',
    'HI':'Hawaii',
    'ID':'Idaho',
    'IL':'Illinois',
    'IN':'Indiana',
    'IA':'Iowa',
    'KS':'Kansas',
    'KY':'Kentucky',
    'LA':'Louisiana',
    'ME':'Maine',
    'MD':'Maryland',
    'MH':'Marshall Islands',
    'MA':'Massachusetts',
    'MI':'Michigan',
    'FM':'Micronesia',
    'MN':'Minnesota',
    'MS':'Mississippii',
    'MO':'Missouri',
    'MT':'Montana',
    'NE':'Nebraska',
    'NV':'Nevada',
    'NH':'New Hampshire',
    'NJ':'New Jersey',
    'NM':'New Mexico',
    'NY':'New York',
    'NC':'North Carolina',
    'ND':'North Dakota',
    'MP':'Northern Marianas',
    'OH':'Ohio',
    'OK':'Oklahoma',
    'OR': 'Oregon',
    'PW':'Palau',
    'PA':'Pennsylvania',
    'PR':'Puerto Rico',
    'RI':'Rhode Island',
    'SC':'South Carolina',
    'SD':'South Dakota',
    'TN':'Tennessee',
    'TX':'Texas',
    'UT':'Utah',
    'VT':'Vermont',
    'VA':'Virginia',
    'VI':'Virgin Islands',
    'WA':'Washington',
    'WV':'West Virginia',
    'WI':'Wisconsin',
    'WY':'Wyoming'}

    try:
        return stateDict[rep['state']]
    except KeyError:
        return ''
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

def check_null(intent, field):
    if 'value' not in (intent['slots'][field]):
        speech_output = "Sorry I did not understand that."
        should_end_session = False
        session_attributes = {}
        reprompt_text = "Ask a different question"
        card_title = "Find Rep Info"
        #return true if null
        return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
    else:
        return False
