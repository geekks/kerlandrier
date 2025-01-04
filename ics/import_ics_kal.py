import datetime
import sys,os
from git import Repo
import json

# Ajoute le dossier "ressources" au sys.path
git_root = Repo(search_parent_directories=True).working_tree_dir
sys.path.insert(0,   os.path.abspath(  os.path.join(  git_root,'resources/python' ) ) )

from ICS_utils import pull_upcoming_ics_events
from getOaLocation import get_or_create_oa_location
from utils import print_well_json
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
    ics_events = pull_upcoming_ics_events(ics_url)
    print(f"Total number of events on ICS : {len(ics_events)}\n")
    access_token = retrieve_access_token(SECRET_KEY)
    new_events_nbr=0
    logContent=[]
    for i, ics_event in enumerate(ics_events):
        try:
            event_title = ics_event.get('title').get('fr')
            print(f"Processing event N°{i} - '{event_title}'")
            # find if event is already imported. Search by name around start time
            # TO DO : replace this multiple call to API by :
            #   - retrieve all current and future events
            #   - check if uid_externe value exists in list
            uid_externe = get_uid_from_name_date( PUBLIC_KEY,
                                                event_title, 
                                                ics_event.get('timings')[0].get('begin').split("T")[0],
                                                uid_externe=True
                                                )
            eventLog = {
                    "ics-id": i,
                    "uid-externe" : ics_event.get("uid-externe"),
                    "title" : event_title,
                    "url": ics_event.get('onlineAccessLink')
                }
            if not uid_externe  :
                # Get OA location from facebook location infos (locationTXT)
                location_uid = get_or_create_oa_location(ics_event.get('locationTXT'), access_token)
                ics_event.update( {"locationUid": location_uid })
                ics_event.pop( "locationTXT" )
                
                # Creates the event
                response = create_event(access_token, ics_event)
                if response['event']['uid']:
                    eventLog["import_status"] = "New event"
                    new_events_nbr += 1
                    eventLog["OaUrl"] = response['event']['OaUrl']
                else:
                    print( f"Problem for {event_title}" )
                    eventLog["import_status"] = "Error posting event on OA"
                    eventLog["error"]= response

        except Exception as e:
            print(f"Error: {e}")
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