"""_summary_
Function to interact with OpenAgenda API
"""

import sys,os
from git import Repo

# Ajoute le dossier "ressources" au sys.path
git_root = Repo(search_parent_directories=True).working_tree_dir
sys.path.insert(0,   os.path.abspath(  os.path.join(  git_root,'resources/python' ) ) )

import math, random
import requests, json
import time, pytz, dateparser

# Chargement des variables d'environnement
OA_PUBLIC_KEY = os.getenv('OA_PUBLIC_KEY')
OA_SECRET_KEY = os.getenv('OA_SECRET_KEY')
ACCESS_TOKEN_URL = os.getenv('ACCESS_TOKEN_URL')
AGENDA_UID = os.getenv('AGENDA_UID')
TOKEN_FILE_NAME = 'secret_token.json'
TBD_LOCATION_UID = os.getenv('TBD_LOCATION_UID')


def get_nonce():
    """
    A timestamp + random number to be unique for each request, even those in short time interval (with same timestamp)
    """
    nonce = str(int(time.time())) + str(math.floor(random.random()*1000))
    return nonce
    

def retrieve_access_token(oa_secret_key):
    # Vérifier si le jeton existe déjà
    token_file_path = os.path.join(git_root,TOKEN_FILE_NAME)
    if os.path.exists(token_file_path):
        with open(token_file_path, 'r', encoding='utf8') as token_file:
            token_data = json.load(token_file)
            if (
                    token_data
                    and token_data.get("access_token")
                    and token_data.get("endate")
                    and (token_data["endate"] - round(time.time()*1000)) > 0
                ):
                    return token_data["access_token"]
        
        
    # print("Request a new token and save it in secret_token.json")
    headers = {
        "Content-Type": 'application/json',
    }
    body = {
        "grant_type": "client_credentials",
        "code": oa_secret_key,
    }

    try:
        oauth_response = requests.post(ACCESS_TOKEN_URL, json=body, headers=headers)
        oauth_response.raise_for_status()

        token_data = {
            'access_token': oauth_response.json()['access_token'],
            'endate': int(time.time()) + oauth_response.json()['expires_in'] - 600,  # 50m à partir de maintenant
        }

        with open(token_file_path, 'w', encoding='utf8') as token_file:
            json.dump(token_data, token_file)

        return token_data['access_token']

    except requests.exceptions.RequestException as exc:
        print(f"Error retrieving access token: {exc}")
        return None

def get_locations(access_token):

    url = f"https://api.openagenda.com/v2/agendas/{AGENDA_UID}/locations"
    after =0
    all_locations=[]
    while after is not None:
        try:
            headers = {
                    "Content-Type": 'application/json',
                    "access-token": access_token,
                    "nonce": get_nonce()
                    }
            response = requests.get(url, headers=headers, params={'after': after, 'detailed': 1})
            response.raise_for_status()
            locations_part=json.loads(response.text)
            all_locations.extend(locations_part.get('locations'))
            after=locations_part.get('after')

        except requests.exceptions.RequestException as exc:
            print(f"Error retrieving locations: {exc}")
            return None
    return all_locations

def post_location(access_token, name, adresse):
    """
    Create a new location in OpenAgenda, using OA Geocoder with 'name' and 'address' as search parameters
    Args:
        access_token (str): The access token obtained by calling `retrieve_access_token`
        name (str): The name of the new location
        adresse (str): The address of the new location
    Returns:
        JSON of the created location, under the key 'location'
    """
    headers = {
        "Content-Type": 'application/json',
        "access-token": access_token,
        "nonce": get_nonce(),
    }
    body = {
        "name": name,
        "address": adresse,
        "countryCode": "FR",
        "state": 0,  # signifie "non vérifié"
    }
    url = f"https://api.openagenda.com/v2/agendas/{AGENDA_UID}/locations"

    try:
        response = requests.post(url, json=body, headers=headers)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as exc:
        text_json = json.loads(exc.response.text)
        if  text_json.get('message') != "geocoder didn't find address":
            print(f"Error Posting location on OA: {exc}")
        #else:
            # print("No existing address found by OA API")
        return None

def patch_location(access_token:str, location_uid: str, body: dict):
    """
    Modify an  OpenAgenda location using a PATCH call. Only modified parameters are needed.
    Args:
        access_token (str): The access token obtained by calling `retrieve_access_token`
        location_uid (str): The uid of the location
        body (dict): parameters to be updated. 
                {"uid"="aaa",{"description":{"fr":"AVEN"}}}
    }
    Returns:
        JSON of the updated location
    """
    headers = {
        "Content-Type": 'application/json',
        "access-token": access_token,
        "nonce": get_nonce(),
    }
    if (type(body) is not dict): 
        raise TypeError("body must be a dict")
    url = f"https://api.openagenda.com/v2/agendas/{AGENDA_UID}/locations/{location_uid}"

    try:
        response = requests.patch(url, json=body, headers=headers)
        response.raise_for_status()
        return response.json().get('location')

    except requests.exceptions.RequestException as exc:
        print(f"Error Patching location on OA: {exc}")
        return None


def delete_location(access_token, location_uid):
    headers = {
        "Content-Type": 'application/json',
        "access-token": access_token,
        "nonce": get_nonce(),
    }
    url = f"https://api.openagenda.com/v2/agendas/{AGENDA_UID}/locations/{location_uid}"

    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as exc:
        print(f"Error deleting location: {exc}")
        return None


def get_events( params: dict):
    """
    Retrieve events from OpenAgenda API with given parameters.
    Args:
        params (dict): The parameters to pass to the API call.
            https://developers.openagenda.com/10-lecture/
            exemple: {'relative[]': 'current',
                    'search': 'conference',
                    'detailed': 1,
                    'monolingual': 'fr'}
    Returns:
        A list of events, or None if an error occurs.
    """
    headers = {
        "Content-Type": 'application/json',
        "nonce": get_nonce()
    }
    url = f"https://api.openagenda.com/v2/agendas/{AGENDA_UID}/events?key={OA_PUBLIC_KEY}"
    after =0
    all_events=[]
    while after is not None:
        try:
            paramsUp =  params | {'after': after} if after != 0 else params
            response = requests.get(url,headers=headers,params=paramsUp)
            response.raise_for_status()
            events_part=json.loads(response.text)
            all_events.extend(events_part.get('events'))
            after=events_part.get('after')
        except requests.exceptions.RequestException as exc:
            print(f"Error getting events: {exc}")
            return None
    return all_events


def create_event(access_token, event, image_path=None):
    headers = {
        "Content-Type": "application/json",
        "access-token": access_token,
        "nonce": get_nonce(),
    }
    body = event
    url = f"https://api.openagenda.com/v2/agendas/{AGENDA_UID}/events"
    # files = None
    # if image_path:
    #     with open(image_path, 'rb') as img_file:
    #         files = {'image': img_file}
    try:
        event_creation_response = requests.post(url, json=body , headers=headers)
        
        if event_creation_response.status_code != 200:
            print(f"Error creating event {event.get('title').get('fr')}: Status Code {event_creation_response.status_code}")
            print(f"Response:")
            print(json.dumps(event_creation_response.json(), indent=4))
            return None
        createdEvent= json.loads(event_creation_response.text)['event']
        print('event "'+ event['title']['fr'] + '" created with uid: ' + str(createdEvent['uid']) )
        # Print OA URL if location is set to DEFAULT to post manually correct it
        if str(createdEvent['location']['uid']) == TBD_LOCATION_UID:
            print("OA event URL: "+ "https://openagenda.com/kerlandrier/contribute/event/"+str(createdEvent['uid']))
        
        return  event_creation_response.json()

    except requests.exceptions.RequestException as exc:
        print(f"Error creating event {event.get('title').get('fr')}: {exc}")
        return None

def patch_event(access_token, eventUid, eventData):
    headers = {
        "Content-Type": "application/json",
        "access-token": access_token,
        "nonce": get_nonce(),
    }
    body = eventData
    url = f"https://api.openagenda.com/v2/agendas/{AGENDA_UID}/events/{eventUid}"
    try:
        event_creation_response = requests.post(url, json=body , headers=headers)
        
        if event_creation_response.status_code != 200:
            print(f"Error pathcing event: Status Code {event_creation_response.status_code}")
            print(f"Response:")
            print(json.dumps(event_creation_response.json(), indent=4))
            return None
        return  event_creation_response.text['event']['uid']

    except requests.exceptions.RequestException as exc:
        print(f"Error creating event: {exc}")
        return None

def delete_event(access_token, event_uid):
    headers = {
        "Content-Type": 'application/json',
        "access-token": access_token,
        "nonce": get_nonce(),
    }
    url = f"https://api.openagenda.com/v2/agendas/{AGENDA_UID}/events/{event_uid}"

    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as exc:
        print(f"Error deleting event: {exc}")
        return None

def search_events( pub_key: str, search_string:str, past_events:bool  = False, other_params:dict = None ) -> dict | None:
    """
    Search events in the OpenAgenda API by a given search string.
    """
    headers = {
        "Content-Type": 'application/json',
        "key": pub_key,
    }
    params = {
        "search": search_string,
        "detailed": 1,
        "monolingual":"fr",
        "nonce": get_nonce()
    }
    if other_params is not None: params.update(other_params)
    if past_events is False : params['relative'] = ["current", "upcoming"]
    
    url = f"https://api.openagenda.com/v2/agendas/{AGENDA_UID}/events"
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as exc:
        print(f"Error getting events: {exc}")
        return None

def get_uid_from_name_date(pub_key: str ,event_name:str, text_date:str = None, uid_externe:bool = False) -> str|None:
    date = dateparser.parse(text_date)
    paris_zone = pytz.timezone('Europe/Paris')
    if date and date.tzinfo != 'Europe/Paris': date = date.astimezone(paris_zone)
    if date: 
        params={"timings":{
                        # TO DO: dynamic change in summer/winter time
                        "gte": date.strftime("%Y-%m-%dT00:00:00+02:00"),
                        "lte": date.strftime("%Y-%m-%dT23:59:59+02:00")
                        }
                    }

    search_result = search_events( pub_key,  event_name, past_events=True, other_params=params)
    if search_result and search_result["events"]: 
        uid= search_result["events"][0].get("uid-externe") if uid_externe else search_result["events"][0].get("id")
        return uid
    return None

#####################
## Tests:
#####################

searchParamsTests = [
                    {
                    'relative[0]': 'current',
                    'detailed': 1,
                    'monolingual': 'fr'},
                    {
                    'relative[0]': 'current',
                    # 'relative[1]': 'upcoming',
                    'search': 'concert',
                    'detailed': 1,
                    'monolingual': 'fr'},
                    {
                    'relative[1]': 'upcoming',
                    'search': 'concert',
                    'detailed': 1,
                    'monolingual': 'fr'},
    
]

if __name__ == "__main__":
    for index, paramTest in enumerate(searchParamsTests):
        print( "--- parmas test n°" + str(index) + "---" )
        events = get_events(paramTest)
        print("nombre d'events: ",len(events))
        if len(events) == 0: continue
        print("Noms: ")
        events_title =[]
        for event in events:
            events_title.append(event.get('uid-externe') if event.get('uid-externe') else event.get('title'))
        print(*events_title,  sep="; ")
            