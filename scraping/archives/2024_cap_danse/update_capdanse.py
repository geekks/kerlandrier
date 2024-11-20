"""_summary_
Add Cap Danse events V2 (with time, description and images)

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
from getAaLocation import get_corresponding_oa_location

from slugify import slugify

access_token = retrieve_access_token(secret_key)

file_name="/var/www/Kerlandrier/scraping/archives/2024_cap_danse/2024_capdanse.csv"
all_events = read_csv(file_name)

def create_CAPDanse_OA_event(event:dict)->dict:
    """Get data from existing CapDanse csv and scraping of each event. Returns Dict with OA keys"""
    if event.get('keywords') != "CAP DanseExposition":
        event_url=event.get('links')
        location_uid = get_corresponding_oa_location(event.get('location').replace('CONCARNEAU', '')) #Avoid direct match with Location "CONCARNEAU"
        resume=get_string_from_webpage(event_url,"#head-event > div > div > p.mention")
        long_description=get_string_from_webpage(event_url,"#content-event > div.rangee > div.col60.ecart-normal > p")[:9000] # 10 000 characters max
        short_description=long_description.split("\n")[0][:150] # 200 characters max in short description
        date_begin=get_datetime_from_text(event.get('date')).replace(year=2024) # Keeps day & month but avoid assigning the wrong year. 
        duree=get_string_from_webpage(event_url,"#sidebar > div.bloc-infos-sidebar > div > p:nth-child(2)") # Get duration from text field like "2h30"
        date_end=get_end_date(date_begin, duree)
        # Special webpage structure for event Id = 20
        if (int(event.get('Id')) == 20):
            selector = "#head-event > div > img"
            imgTag= 'src'
        else:
            selector = "#head-event > div > picture > img"
            imgTag= 'data-lazy-src'
        imageURL = get_image_from_webpage(url = event_url,
                                selector = selector,
                                imgTag= imgTag,
                                path = None,
                                )
        
        eventOA= {
                    "uid-externe": event.get('Id') + "-" + slugify(event.get('title')),
                    "title": { "fr": event.get('keywords') + " / "  + " " + event.get('title') ,
                            "en": event.get('keywords')  + " " + event.get('title') } ,
                    "summary": { "fr": resume },
                    "description": { "fr": short_description, "en": short_description  },
                    "locationUid": int(location_uid),
                    "links": event_url,
                    "longDescription": event_url + os.linesep + long_description,   
                    "keywords": {
                                "fr": ["CapDanseEvent", "CapDanse", "danse"]
                                },
                    "timings": [
                            {
                            "begin": date_begin.isoformat(),
                            "end": date_end.isoformat()
                            },
                            ],
                    "onlineAccessLink": event_url,
                    "image": {"url": imageURL}
                }
        return eventOA
    else:
        return None

# First create a Json file with all valid events
OAEvents=[]
for event in all_events:
    oa_event = create_CAPDanse_OA_event(event)
    if oa_event:
        OAEvents.append(oa_event)
    save_dict_to_json_file(OAEvents, "eventsCapDanse2ToPost.json")

# Then post them and saved them (with attributed unique ID form OA) in a json file
# to update them or restart from last success in case of failing
saved_events_capv2={}
with open('eventsCapDanse2ToPost.json') as json_file:
    eventsv2 = json.load(json_file)
for event in eventsv2:
    response = create_event(access_token,event = event, image_path = None)
    uid = response['event']['uid'] if response['event'] else event['uid-externe'] 
    saved_events_capv2[response['event']['uid'] ] = event
    save_dict_to_json_file(saved_events_capv2, "eventsCapDanse2Created.json")

