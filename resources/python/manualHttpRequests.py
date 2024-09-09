"""_summary_
Function to interact with OpenAgenda API
"""

import math, random
import os
import requests, json
import time

# Chargement des variables d'environnement
public_key = os.getenv('OA_PUBLIC_KEY')
secret_key = os.getenv('OA_SECRET_KEY')
ACCESS_TOKEN_URL = os.getenv('ACCESS_TOKEN_URL')
AGENDA_UID = os.getenv('AGENDA_UID')
token_file_path = './secret_token.json'
TBD_LOCATION_UID = os.getenv('TBD_LOCATION_UID')


def get_nonce():
    """
    Purpose: get a timestamp + random number to be unique for each request, even those in short time interval (with same timestamp)
    """
    nonce = str(int(time.time())) + str(math.floor(random.random()*1000))
    return nonce
    

def retrieve_access_token(api_secret_key):
    # Vérifier si le jeton existe déjà
    if os.path.exists(token_file_path):
        with open(token_file_path, 'r', encoding='utf8') as token_file:
            token_data = json.load(token_file)

        if 'access_token' in token_data and 'endate' in token_data and time.time() - token_data['endate'] < 3600:
            return token_data['access_token']
        
    print("Request a new token and save it in secret_token.json")
    headers = {
        "Content-Type": 'application/json',
    }
    body = {
        "grant_type": "client_credentials",
        "code": api_secret_key,
    }

    try:
        oauth_response = requests.post(ACCESS_TOKEN_URL, json=body, headers=headers)
        oauth_response.raise_for_status()

        token_data = {
            'access_token': oauth_response.json()['access_token'],
            'endate': time.time() + 3600,  # 1 heure à partir de maintenant
        }

        with open(token_file_path, 'w', encoding='utf8') as token_file:
            json.dump(token_data, token_file)

        return token_data['access_token']

    except requests.exceptions.RequestException as exc:
        print(f"Error retrieving access token: {exc}")
        return None

def get_locations(access_token):
    headers = {
        "Content-Type": 'application/json',
        "access-token": access_token,
        "nonce": get_nonce(),
    }
    url = f"https://api.openagenda.com/v2/agendas/{AGENDA_UID}/locations"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as exc:
        print(f"Error retrieving locations: {exc}")
        return None

def post_location(access_token, name, adresse):
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
        if exc.response and exc.response.status_code == 400 and exc.response.json().get('message') == "geocoder didn't find address":
            print("No existing address found by OA API")
        else:
            print(f"Error OA Post location: {exc}")
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

def get_events(public_key, params: dict):
    headers = {
        "Content-Type": 'application/json',
        "nonce": get_nonce()
    }
    url = f"https://api.openagenda.com/v2/agendas/{AGENDA_UID}/events?key={public_key}"
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as exc:
        print(f"Error getting events: {exc}")
        return None

def create_event(access_token, event):
    headers = {
        "Content-Type": 'application/json',
        "access-token": access_token,
        "nonce": get_nonce(),
    }
    body = event
    url = f"https://api.openagenda.com/v2/agendas/{AGENDA_UID}/events"

    try:
        event_creation_response = requests.post(url, json=body, headers=headers)
        
        # Vérifie si le code de statut n'est pas 200
        if event_creation_response.status_code != 200:
            print(f"Error creating event: Status Code {event_creation_response.status_code}")
            print(f"Response:")
            print(json.dumps(event_creation_response.json(), indent=4))
            return None

        return event_creation_response.json()

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
