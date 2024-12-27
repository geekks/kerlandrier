"""_summary_
Main Function to get incoming events from FB private calendar
"""

import sys,os
from git import Repo

# Ajoute le dossier "ressources" au sys.path
git_root = Repo(search_parent_directories=True).working_tree_dir
sys.path.insert(0,   os.path.abspath(  os.path.join(  git_root,'resources/python' ) ) )

import requests
from ics import Calendar
from datetime import datetime, timedelta
from slugify import slugify
from scraping_utils import strip_html
import unicodedata

def pull_upcoming_ics_events(ics_url: str)-> list[dict]:
    """
    Fetch upcoming events from an ICS file.
    """
    upcoming_ics_events = []
    
    # Fetch and parse the ICS file
    response = requests.get(ics_url)
    response.raise_for_status()
    calendar = Calendar(  response.text.replace('\"', "'" ))

    for ics_event in calendar.events:
        timings = []
        
        # Check if the event is in the future
        if ics_event.end.int_timestamp > datetime.timestamp(datetime.now()):
            # Handle timings (split into max 24h intervals if needed)
            event_duration = ics_event.end - ics_event.begin
            if event_duration < timedelta(hours=24):
                timings.append({
                    "begin": ics_event.begin.isoformat(),
                    "end": ics_event.end.isoformat()
                })
            else:
                # Split into 24-hour intervals
                begin = ics_event.begin
                end = ics_event.end
                while begin < end:
                    next_end = min(begin + timedelta(hours=24), end)
                    timings.append({
                        "begin": begin.isoformat(),
                        "end": next_end.isoformat()
                    })
                    begin = next_end

            # Clean up the event description
            description =  unicodedata.normalize('NFKC', ics_event.description) if hasattr(ics_event, "description") else ""
            short_description=description.split("\n")[0][:150] # 200 characters max in short description
            
            # Prepare the OpenAgenda event structure
            new_oa_event = {
                "uid-externe": ics_event.uid,
                "slug": slugify(ics_event.name),
                "title": {"fr": unicodedata.normalize('NFKC', ics_event.name)},
                "description": {"fr": f"{short_description or ''}"},
                "locationTXT": ics_event.location,
                "longDescription": {"fr": description},
                "timings": timings,
                "onlineAccessLink": ics_event.url if hasattr(ics_event, "url") else None,
                "attendanceMode": 3,  # 1: physical, 2: online, 3: hybrid
            }
            upcoming_ics_events.append(new_oa_event)
    
    return upcoming_ics_events