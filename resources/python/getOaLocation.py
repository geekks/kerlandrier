"""_summary_
Functions to manage locations with OA API
"""

import sys
import os
import git

# Ajoute le dossier "ressources" au sys.path
git_root = git.Repo(search_parent_directories=True).working_tree_dir
sys.path.insert(0,   os.path.abspath(  os.path.join(  git_root,'resources/python' ) ) )

from utils import *
from scraping_utils import *
from HttpRequests import post_location, retrieve_access_token, delete_location, get_locations

from thefuzz import fuzz
from thefuzz import process
import re

# Environment variables
TBD_LOCATION_UID = os.getenv("TBD_LOCATION_UID")


def get_or_create_oa_location(searched_location:str, access_token: str)->str:
    """
    Tries to find a matching OpenAgenda location for the given searched location.
    Returns an OALocation UID (found, created or default one.)
    """
    print("Searching location for : '"+ searched_location +"'")
    
    allOaLocations = get_locations(access_token)
    if not searched_location or not allOaLocations:
        print("[ERROR] inputLocation is null or OA Locations list is empty")
        return None
    
    # 0) Use optimized searched, removing false positives
    optimized_searched_location=re.sub(r'\b(?:concarneau|(?:29|56)\d{3})\b',
                                            '',
                                            searched_location,
                                            flags=re.IGNORECASE
                                            )
    
    # 1) Try to find an existing OALocation
    OaLocationsIndex = {}
    for location in allOaLocations:
        OaLocationsIndex[location["uid"]]=location['name'] + " " + location['address']
    # returns a list of tuples (name adress , score , OAuid)
    results = process.extract(optimized_searched_location, OaLocationsIndex, scorer=fuzz.token_set_ratio) or []
    if results[0] and results[0][1] > 85:  # Best matching score >85
        print(f"- match with {results[0] }")
        return results[0][2]

    # 2) Try to create an OALocation
    response = post_location(access_token, searched_location, searched_location)
    if not response or not response.get('location', {}).get('uid'):
        print("-> Returning location 'To be defined' (Could not create location on OpenAgenda)")
        return TBD_LOCATION_UID

    # Stay in rectangle covering Breizh
    new_oa_location = response['location']
    lat = new_oa_location['latitude']
    long = new_oa_location['longitude']
    if ( new_oa_location.get('uid')        
        and 47 < float(lat) < 49
        and -5.5 < float(long) < -1 
        ):
        print(f"-> New OA location created : {new_oa_location['name']}, {new_oa_location['address']}")
        return new_oa_location['uid']
    else:
        delete_location(access_token, new_oa_location['uid'])
        print(f"->  Location not in Breizh: returning 'To be defined' location")
        return TBD_LOCATION_UID

def get_locations_list(searched_location:str, access_token: str)->list:
    """
    Return list of matching locations in format ('NAME, ADRESS, SCORE [0-100], UID)
    """
    allOaLocations = get_locations(access_token)
    if not searched_location or not allOaLocations:
        print("[ERROR] inputLocation is null or OA Locations list is empty")
        return None
    
    # 1) Try to find an existing OALocation
    OaLocationsIndex = {}
    for location in allOaLocations:
        OaLocationsIndex[location["uid"]]=location['name'] + " " + location['address']
    # returns a list of tuples (name adress , score , OAuid)
    results = process.extract(searched_location, OaLocationsIndex, scorer=fuzz.token_set_ratio) or []
    
    
    if len(results): 
        if results[0][1] >= 80:  # Best matching score >85
            return results[0]
        # good_results = [item for item in results if item["score"] > 70]
        return results[:5]
    else:
        return None

#####################
## Test cases:
#####################

locations_examples = [
    {"input_location": 'MJC Tregunc Le Sterenn, Rue Jacques Prévert, 29910 Trégunc, France'},
    {"input_location": 'Explore'},
    {"input_location": "Bar de Test, 1 Pl. de l'Église, 29100 Pouldergat"}, # Lieu inexistant mais ville existante
    {"input_location": 'qsdfg'}, # Texte aléatoire
    {"input_location": '30 Rue Edgar Degas, 72000 Le Mans'}, # HOrs Bretagne
    {"input_location": '11 Lieu-dit Quilinen 29510 Landrévarzec'}, # Non répertorié sur OA
    {"input_location": 'La Loco'},
    {"input_location": 'Boulevard de la Gare, Quimperlé'},
    {"input_location": 'La Caserne Concarneau '},
    {"input_location": '1 avenue Docteur NICOLAS, Concarneau'},
    {"input_location": 'Intermarché Concarneau (Route de Trégunc, Concarneau)'}
]

def test_locations(location_array):
    SECRET_KEY = os.getenv("OA_SECRET_KEY")
    access_token = retrieve_access_token(SECRET_KEY)
    
    nbr_locations= len(get_locations(access_token))
    print(f"Number of locations: {nbr_locations}")
    for loc in location_array:
        optimized_searched_location=re.sub(r'\b(?:concarneau|(?:29|56)\d{3})\b',
                                            '',
                                            loc['input_location'],
                                            flags=re.IGNORECASE
                                            )
        uid = get_or_create_oa_location( optimized_searched_location,access_token)
        print("--------------\n")

if __name__ == "__main__":
    test_locations(locations_examples)
