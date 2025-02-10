
import pprint
import sys,os
from git import Repo

# Ajoute le dossier "ressources" au sys.path
git_root = Repo(search_parent_directories=True).working_tree_dir
sys.path.insert(0,   os.path.abspath(  os.path.join(  git_root,'resources/python' ) ) )

from HttpRequests import (  retrieve_access_token,
                            get_locations,
                            patch_location)

AGENDA_UID = os.getenv('AGENDA_UID')
BASE_URL = "https://api.openagenda.com/v2/"
OA_SECRET_KEY = os.getenv('OA_SECRET_KEY')

def validate_locations():
    accessToken = retrieve_access_token(OA_SECRET_KEY)
    allLocations= get_locations(accessToken)

    if allLocations and len(allLocations) > 0:
        validated_count = 0
        for location in allLocations :
            if location["state"] == 0:
                try:
                    response=patch_location(accessToken, str(location["uid"]), { 'state': 1 })
                    print("Validated location:", location["name"])
                    validated_count += 1
                except Exception as e:
                    print(f"Error validating location: {location["name"]} - {location['uid']}")
                    print(e)
        print("Total validated locations:", validated_count)
        

if __name__ == "__main__":
    validate_locations()