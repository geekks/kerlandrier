"""_summary_
Functions used in different scripts for scraping or interact with OpenAgenda APi
"""

import sys,os
from git import Repo

# Ajoute le dossier "ressources" au sys.path
git_root = Repo(search_parent_directories=True).working_tree_dir
sys.path.insert(0,   os.path.abspath(  os.path.join(  git_root,'resources/python' ) ) )

import datetime
import json, csv
import re

import dateparser
import pytz

def print_well_json(data)->None:
    """ display a well formatted json in console"""
    wellJson= json.dumps(data, indent=4, ensure_ascii=False)
    print(wellJson) 

def save_dict_to_json_file(data_dict:dict, file_name:str)->None:
    """Export the data to a JSON file"""
    with open(file_name, mode="w", encoding='utf8') as file:
        json.dump(data_dict, file, indent=4, ensure_ascii=False)

def read_csv(file_name):
    """Read a CSV file and return a dictionary of Data objects"""
    data_dict = {}
    with open(file_name, "r", encoding='utf-8') as file:
        reader = csv.DictReader(file)
        data_dict = [ row for row in reader]
    return data_dict

def validate_OAevent_format(event:dict) -> bool:
    """
    Raise error if timing, url or keywords is not valid with OA event
    To avoid POST Event to OpenAgenda API
    """
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
    return True

def get_end_date(start_date: datetime.datetime,duree: str) -> datetime.datetime: 
    """
    Get end_date (DateTime) from start_date (DateTime) and duration (Str like "2h 30min")
    Default "duree" if not correct or provided : 2h
    """
    if start_date:
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
                    )
        return end_date
    else:
        raise ValueError("start_date is None")
        return None
