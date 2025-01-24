"""
Script to import events from a private Facebook calendar (ICS file)
"""
import sys,os
from git import Repo
import json

# Ajoute le dossier "ressources" au sys.path
git_root = Repo(search_parent_directories=True).working_tree_dir
sys.path.insert(0,   os.path.abspath(  os.path.join(  git_root,'resources/python' ) ) )

import datetime
from ICS_utils import pull_upcoming_ics_events
from getOaLocation import get_or_create_oa_location
from HttpRequests import get_events
from HttpRequests import( 
        retrieve_access_token,
        get_uid_from_name_date,
        create_event
        )

PUBLIC_KEY = os.getenv("OA_PUBLIC_KEY")
SECRET_KEY = os.getenv("OA_SECRET_KEY")
ICS_URL = os.getenv("ICS_PRIVATE_URL_KLR_FB")

now=datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

def import_ics(ics_url):
    """Main function to import ICS events."""
    # Fetch events from ICS
    
    # TO DO
    # Improve Text rendering, progress bar in console https://rich.readthedocs.io/en/stable/index.html
    
    # TO DO
    # Removed stylished text with weird fonts, like in https://yaytext.com/unstyle/
    # Unidecode ? https://pypi.org/project/Unidecode/

    ics_events = pull_upcoming_ics_events(ics_url)
    print(f"Total number of events on ICS : {len(ics_events)}\n")
    
    eventsOa: list=get_events(params={"relative[0]": "upcoming", "relative[1]": "current", "detailed": 1, "monolingual": "fr"})
    print(f"Total number of future events on Oa : {len(eventsOa)}\n")
    uidsExterneOa = [event["uid-externe"] for event in eventsOa if "uid-externe" in event]
    
    new_events_nbr=0
    logContent=[]
    access_token = retrieve_access_token(SECRET_KEY)
    for i, ics_event in enumerate(ics_events):
        try:
            event_title = ics_event.get('title').get('fr')
            uidExterneIcsEvent = ics_event.get("uid-externe")
            print(f"Processing event N°{i} - '{event_title}'")
            # create event log in case of error
            eventLog = {
                    "ics-id": i,
                    "uid-externe" : uidExterneIcsEvent,
                    "title" : event_title,
                    "url": ics_event.get('onlineAccessLink')
                }
            # find if event is already imported.
            if uidExterneIcsEvent in uidsExterneOa:
                continue
            # Get OA location from facebook location infos (locationTXT)
            location_uid = get_or_create_oa_location(ics_event.get('locationTXT'), access_token)
            ics_event.update( {"locationUid": location_uid })
            ics_event.pop( "locationTXT" )
            
            # Creates the event
            response = create_event(access_token, ics_event)
            if response['event']['uid']:
                eventLog["import_status"] = "New event"
                new_events_nbr += 1
                eventLog["OaUrl"] = "https://openagenda.com/fr/" + response['event']['originAgenda']['slug'] + "/events/" + response['event']['slug']
            else:
                print( f"Problem for {event_title}\n" )
                eventLog["import_status"] = "Error posting event on OA"
                eventLog["error"]= response

        except Exception as e:
            print(f"Error: {e} \n" )
            eventLog["import_status"] = "Error processing event"
            eventLog["error"]=  {e}

        if "import_status" in eventLog : logContent.append( eventLog)
        
    with open(f"ics/import_ics_logs.txt", "a") as log_file:
        log_file.write(now + "\n")
        for dic in logContent:
            json.dump(dic, log_file,indent=2, ensure_ascii=False) 
    print(f"Checked {i+1} events from ICS URL.")
    print(f"{new_events_nbr} new events created")

if __name__ == "__main__":
    import_ics(ICS_URL)
exit(0)