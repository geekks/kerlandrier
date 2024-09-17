"""_summary_"""

import sys
import os

# Ajoute le dossier "ressources" au sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../resources/python')))

from utils import *
from scraping_utils import *
from manualHttpRequests import post_location, retrieve_access_token, delete_location, get_locations

from thefuzz import fuzz
from thefuzz import process
import requests  # Assuming manualHttpRequests functions are HTTP calls, requests will handle this.

# Environment variables
TBD_LOCATION_UID = os.getenv("TBD_LOCATION_UID")
SECRET_KEY = os.getenv("OA_SECRET_KEY")


def search_oa_location_id(input_location, access_token):
    """
    Search a given adress in OA locations DB (using name & adress) with TheFuzz
    Args:
        input_location (str): The event location to search for e.g. "MJC Tregunc Le Sterenn"
    Returns:
        str: An OALocationUid if found, or None otherwise.
    """
    all_oa_locations = get_locations(access_token)
    if not input_location or not all_oa_locations:
        print("[ERROR] inputLocation is null or OA Locations list is empty")
        return None
    short_locations = {}
    for location in all_oa_locations:
        short_locations[location["uid"]]=location['name'] + " " + location['address']
    
    results = process.extract(input_location, short_locations, scorer=fuzz.token_set_ratio) # list of tuples (name adress , score , OAuid)

    if results and results[0][1] > 85:  # Minimum matching score
        print(f"- match with {results[0] }")
        return results[0][2]            # Return OALocationUid
    return None


def get_corresponding_oa_location(searched_location:str)->str:
    """
    Tries to find a matching OpenAgenda location for the given searched location.
    Returns an OALocation UID (found, created or default one.)
    """
    access_token = retrieve_access_token(SECRET_KEY)
    print("Looking for location for : '"+ searched_location +"'")
    # Try to find an existing OALocation
    oa_location = search_oa_location_id(searched_location, access_token)
    if oa_location:
        return oa_location
    elif searched_location:
        # Try to create an OALocation
        response = post_location(access_token, searched_location.split(",")[0], searched_location)

        if not response or not response.get('location', {}).get('uid'):
            print("-> Returning location 'To be defined' (Could not create location on OpenAgenda)")
            return TBD_LOCATION_UID

        new_oa_location = response['location']
        lat = new_oa_location['latitude']
        long = new_oa_location['longitude']

        if (
            new_oa_location.get('uid')
            # Rectangle covering Breizh
            and 47 < float(lat) < 49
            and -5.5 < float(long) < -1
        ):
            print(f"-> New OA location created : {new_oa_location['name']}, {new_oa_location['address']}")
            return new_oa_location['uid']
        else:
            data = delete_location(access_token, new_oa_location['uid'])
            print(f"->  Location not in Breizh: returning 'To be defined' location")
            return TBD_LOCATION_UID
    else:
        return TBD_LOCATION_UID

# # Example usage:
# locations_examples = [
#     {"input_location": 'MJC Tregunc Le Sterenn, Rue Jacques Prévert, 29910 Trégunc, France'},
#     {"input_location": 'Explore'},
#     {"input_location": "Bar de Test, 1 Pl. de l'Église, 29100 Pouldergat"},
#     {"input_location": 'qsdfg'},
#     {"input_location": '30 Rue Edgar Degas, 72000 Le Mans'},
#     {"input_location": '11 Lieu-dit, Quilinen, 29510 Landrévarzec'}
# ]

# def test_locations(location_array):
#     for loc in location_array:
#         print(f"Searching for {loc['input_location']}")
#         test_uid = get_corresponding_oa_location(loc['input_location'])
#         print(f"Matching --> OA Uid= {test_uid}")
#         print("--------------\n")

# # Run the test
# test_locations(locations_examples)
