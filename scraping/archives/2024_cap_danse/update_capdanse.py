"""_summary_
Add Cap Danse events V2 (with time and images)

"""

import sys
import os

# Ajoute le dossier "ressources" au sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../resources/python')))

from utils import *
from scraping_utils import *
from manualHttpRequests import *

import datetime
import re

file_name="/var/www/Kerlandrier/scraping/2024_cap_danse/2024_capdanse.csv"

def create_events(data_dict:dict):
    """Create events from data"""
    description=get_string_from_webpage(data_dict.links,"#content-event > div.rangee > div.col60.ecart-normal")
    date_begin=get_iso_date_from_text(data_dict.date)
    duree=get_string_from_webpage(data_dict.links,"#sidebar > div.bloc-infos-sidebar > div:nth-child(1) > p:nth-child(2)")
    date_end=get_end_date_from_start_and_duration(date_begin, duree)
    imageFullPath = download_image_from_webpage(url = data_dict.url,
                            selector = "#head-event > div > picture > img",
                            imgTag= 'data-lazy-src',
                            path = os.getcwd()+"/scraping/2024_cap_danse/images/",
                            )
    events=[]
    for event_data in data_dict:
        if event_data.keywords != "CAP DanseExposition":
            eventOA= {
                        "uid-externe": str(math.floor(random.random()*1000)),
                        "title": event_data.keywords + " " + event_data.title,
                        "summary": { "fr": "Résumé" },
                        "description": { "fr": description },
                        "locationUid": "lieu",
                        "links": "url",
                        "longDescription":  "",   
                        "keywords": {
                                    "fr": ["musique", "concert", "rock"]
                                    },
                        "timings": [
                                {
                                "begin": date_begin,
                                "end": date_end
                                },
                                ],
                        "onlineAccessLink": "url",
                        "image": {
                            "url" : "https://i.pinimg.com/originals/d1/d9/ae/d1d9aec6e351baa115000b4b75e02b1b.jpg"
                        }
                    }
            events.append(eventOA)
    return events





def get_end_date_from_start_and_duration(start_date: datetime,duree: str): 
    if duree & start_date:
        pattern_xhy = r'(\d+)h(\d+)?'
        pattern_ymin = r'(\d+) ?min'
        hours=2
        minutes=0
        if re.match(pattern_xhy, duree):
            hours   = int( re.match(pattern_xhy, duree).group(1) or 0)
            minutes = int( re.match(pattern_xhy, duree).group(2) or 0)
        elif re.match(pattern_ymin, duree):
            minutes = int( re.match(pattern_ymin, duree).group(1) or 0)
        hr =( hours, minutes)
        end_date=   ( start_date
                        + datetime.timedelta(hours=hr[0], minutes=hr[1] )
                    ).isoformat()
        return end_date
    else:
        return None


# for event in events_dict:
#     start_date=dateparser.parse(event.get('date'))
#     if (event.get('keywords') not in ["CAP DanseExpositionSpectacle", "CAP DanseExposition"]) and start_date:
#         duree=get_string_from_webpage(event.get('links'),"#sidebar > div.bloc-infos-sidebar > div:nth-child(1) > p:nth-child(2)")
#         end_date=get_end_date_from_start_and_duration(start_date,duree)
    



# start_date ? =get_string_from_webpage("https://www.danseatouslesetages.org/action-artistique/masterclass/",
#                         "#content-event > div.rangee > div.col60.ecart-normal",
#                         )



def retrieve_existing_capdase_events(access_token, search):
    access_token = retrieve_access_token(secret_key)
    if access_token:
        parameters = {
                'search': search
                }
        events_result = get_events(public_key, parameters)
        filtered_events_cap = []
        for event in events_result['events']:
            oa_ID = int(event["uid-externe"].replace("import_csv_raw_2024_cap_danse_",''))
            data = {
                "keywords": event["keywords"]["fr"][0] or "",
                "uid": event["uid"],
                "oa_ID": oa_ID,
                "title": event["title"]["fr"],
                "description": event["description"]["fr"],
                }
            filtered_events_cap.append(data)
        # print_well_json(filtered_events_cap)
        sorted_events_cap = sorted(filtered_events_cap, key=lambda x: x["oa_ID"])
        print( "Nombre d'events: " + str(filtered_events_cap.__len__()))
        with open("events_cap.json", 'w', encoding='utf8') as events_file:
            json.dump(sorted_events_cap, events_file)
