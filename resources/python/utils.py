"""_summary_
Functions used in different scripts for scraping or interact with OpenAgenda APi
"""

import datetime
import json

import dateparser
import pytz

def print_well_json(data):
    """
    Purpose: display a well formatted json in console
    """
    wellJson= json.dumps(data, indent=4)
    print(wellJson) 

def save_dict_to_json(data_dict:dict, file_name:str):
    """Export the data to a JSON file"""
    with open(file_name, "w") as file:
        json.dump(data_dict, file, indent=4)

def validate_event_data(event):
    """Validate the event data and structure"""
    # Example validation: check if date is longer than 5 caracters
    for  timing in event.get("timings") :
        print( "timing_begin",timing.get("begin"))
        parsedDateBegin = dateparser.parse(timing.get("begin"))
        parsedDateEnd = dateparser.parse(timing.get("end"))
        now = datetime.datetime.now(pytz.timezone("Europe/Paris"))
        if (parsedDateBegin <  now) or (parsedDateEnd >  now):
            raise ValueError(f"Error: event  {event.get('title')} not in past. Start : {parsedDateBegin}, End : {parsedDateEnd}")
    # Example validation: check if keywords are not empty
    if not event.get("keywords"):
        raise ValueError(f"Empty keywords: {event.get("keywords")}")
    if "https://" not in event.get("links"):
        raise ValueError(f"URL not valid: {event.get("links")}")
    return event