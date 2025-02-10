"""_summary_
Functions used in different scripts for scraping or interact with OpenAgenda APi
"""

import sys,os
from git import Repo

# Ajoute le dossier "ressources" au sys.path
git_root = Repo(search_parent_directories=True).working_tree_dir
sys.path.insert(0,   os.path.abspath(  os.path.join(  git_root,'resources/python' ) ) )

from datetime import datetime, timedelta, date
import json, csv
import re

import dateparser
import pytz

from difflib import SequenceMatcher
from wasabi import color

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
        now = datetime.now(pytz.timezone("Europe/Paris"))
        if (parsedDateBegin <  now) or (parsedDateEnd >  now):
            raise ValueError(f"Error: event  {event.get('title')} not in past. Start : {parsedDateBegin}, End : {parsedDateEnd}")
    # Example validation: check if keywords are not empty
    if not event.get("keywords"):
        raise ValueError(f"Empty keywords: {event.get("keywords")}")
    if "https://" not in event.get("links"):
        raise ValueError(f"URL not valid: {event.get("links")}")
    return True

def get_end_date(start_date: datetime,duree: str) -> datetime: 
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
                        + timedelta(hours=hr[0], minutes=hr[1] )
                    )
        return end_date
    else:
        raise ValueError("start_date is None")
        return None

def showDiff(a:str, b:str):
    output = []
    matcher = SequenceMatcher(None, a, b)
    for opcode, a0, a1, b0, b1 in matcher.get_opcodes():
        if opcode == "equal":
            output.append(a[a0:a1])
        elif opcode == "insert":
            output.append(color(b[b0:b1], fg=16, bg="green"))
        elif opcode == "delete":
            output.append(color(a[a0:a1], fg=16, bg="red"))
        elif opcode == "replace":
            output.append(color(b[b0:b1], fg=16, bg="green"))
            output.append(color(a[a0:a1], fg=16, bg="red"))
    return "".join(output)

def convertDate(date_obj:date|datetime, period:str)->datetime:
    if isinstance(date_obj, datetime):
        return date_obj
    elif isinstance(date_obj, date):
        datetime_obj = datetime.combine(date_obj, datetime.min.time())
        pytz.timezone("Europe/Paris").localize(datetime_obj)
        if period == "start":
            return datetime_obj.replace(hour=10, minute=30)
        elif period == "end":
            return datetime_obj.replace(hour=17, minute=30)
        else:
            raise ValueError(f"period parameter \'{period}\' is not valid or must be defined")
    else:
        raise ValueError(f"date_obj {date_obj} is not a date or datetime object")