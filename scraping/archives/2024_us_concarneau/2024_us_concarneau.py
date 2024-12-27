"""_summary_
Add US Concarneau events

"""

import sys
import os
import git

# Ajoute le dossier "ressources" au sys.path
git_root = git.Repo(search_parent_directories=True).working_tree_dir
sys.path.insert(0,   os.path.abspath(  os.path.join(  git_root,'resources/python' ) ) )

from utils import *
from scraping_utils import *
from HttpRequests import *
from getOaLocation import get_corresponding_oa_location

from slugify import slugify

access_token = retrieve_access_token(secret_key)
script_folder= os.path.join(git_root, "scraping/2024_us_concarneau/")
file_name="20240926_usc-concarneau.com.csv"
all_events = read_csv(script_folder+file_name)

def create_OA_event(event:dict)->dict:
    """Get data from existing csv and scraping of each event. Returns Dict with OA keys"""
    date_begin=get_datetime_from_text(event.get('data-date') ) 
    previous_imported_date=pytz.timezone('Europe/Paris').localize(datetime.datetime(2024,11,1))
    if (event.get('data-home') == "Concarneau" and date_begin > previous_imported_date): # Juste les matchs à domicile
        event_url="https://billetterie-usconcarneau.tickandlive.com/"
        location_uid = get_corresponding_oa_location("stade Guy Piriou")
        resume="Concarneau vs " + event.get('data-away') + " au stade Guy Piriou"
        date_begin=get_datetime_from_text(event.get('data-date') + " " + event.get('data-time')) 
        duree="2h"
        date_end=get_end_date(date_begin, duree)
        unique_id = slugify(event.get('data-home') + "-" +  event.get('data-away')+ "-" + str(date_begin.year))

        eventOA= {
                    "uid-externe": unique_id,
                    "title": { "fr": resume } ,
                    "monolingual": "fr",
                    "summary": { "fr": resume },
                    "description": { "fr": resume  },
                    "locationUid": int(location_uid),
                    "keywords": {
                                "fr": ["AllezLesThoniers"]
                                },
                    "timings": [
                            {
                            "begin": date_begin.isoformat(),
                            "end": date_end.isoformat()
                            },
                            ],
                    "onlineAccessLink": event_url,
                }
        return eventOA
    else:
        return None

# First create a Json file with all valid events
oa_events_to_post="eventsToPost.json"
OAEvents=[]
for event in all_events:
    oa_event = create_OA_event(event)
    if oa_event:
        OAEvents.append(oa_event)
    save_dict_to_json_file(OAEvents, script_folder + oa_events_to_post)

input("Check content of eventsToPost.json and press Enter to continue...")
# Then post them and saved them (with attributed unique ID form OA) in a json file
# to update them or restart from last success in case of failing
saved_events_capv2={}
saved_events_capv2['events']=[]
with open(script_folder + oa_events_to_post) as json_file:
    eventsv2 = json.load(json_file)
for event in eventsv2:
    response = create_event(access_token,event = event, image_path = None)
    saved_events_capv2['events'].append(response['event'])
    save_dict_to_json_file(saved_events_capv2, script_folder + "eventsCreated.json")

