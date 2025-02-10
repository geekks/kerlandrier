"""_summary_
Main Function to get incoming events from FB private calendar
"""

import sys,os
from git import Repo

# Ajoute le dossier "ressources" au sys.path
git_root = Repo(search_parent_directories=True).working_tree_dir
sys.path.insert(0,   os.path.abspath(  os.path.join(  git_root,'resources/python' ) ) )

import requests
import icalendar
from datetime import datetime, timedelta, date
from slugify import slugify
import re
import unicodedata
from utils import convertDate

class IcsEvent:
    def __init__(self,
                summary="",
                description="",
                location="",
                start_date=None,
                end_date=None,
                url="",
                categories=None,
                status="CONFIRMED"):
        self.summary = summary
        self.description = description
        self.location = location
        self.start_date = start_date if start_date else datetime.now()
        self.end_date = end_date if end_date else datetime.now()
        self.url = url
        self.categories = categories if categories else []
        self.status = status

    def __str__(self):
        return f"IcsEvent: {self.summary} ({self.start_date} - {self.end_date})"

    def to_ics(self):
        # Generate ICS string representation of the event
        ics_string = f"BEGIN:VEVENT\n"
        ics_string += f"SUMMARY:{self.summary}\n"
        ics_string += f"DESCRIPTION:{self.description}\n"
        ics_string += f"LOCATION:{self.location}\n"
        ics_string += f"DTSTART;TZID=UTC:{self.start_date.strftime('%Y%m%dT%H%M%S')}\n"
        ics_string += f"DTEND;TZID=UTC:{self.end_date.strftime('%Y%m%dT%H%M%S')}\n"
        ics_string += f"URL:{self.url}\n"
        ics_string += f"CATEGORIES:{','.join(self.categories)}\n"
        ics_string += f"STATUS:{self.status}\n"
        ics_string += "END:VEVENT\n"
        return ics_string
    def normalizeText(self):
        #to do
        return None

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

def pull_upcoming_ics_events(ics_url: str)-> list[dict]:
    """
    Fetch upcoming events from an ICS file.
    """
    upcoming_ics_events = []
    
    # Fetch and parse the ICS file
    response = requests.get(ics_url)
    response.raise_for_status()
    
    # add default organizer to avoid import error
    # Regex pour capturer le groupe contenant un ":" avant ":MAILTO"
    pattern = r"(CN=.*?:.*?\:MAILTO)"
    icsCleaned =response.text.replace("ORGANIZER:MAILTO", "ORGANIZER;CN=Inconnu:MAILTO")
    icsCleaned = re.sub(pattern, lambda m: m.group(1).replace(":", "-"), icsCleaned)
    calendar =icalendar.Calendar.from_ical(icsCleaned)

    for ics_event in calendar.walk("VEVENT"):
        timings = []
        ics_event_end=convertDate(ics_event.end, "end")
        ics_event_start=convertDate(ics_event.start, "start")
        # Check if the event is in the future
        if datetime.timestamp(ics_event_end) > datetime.timestamp(datetime.now()):
            # Handle timings (split into max 24h intervals if needed)
            event_duration = ics_event.duration
            if event_duration < timedelta(hours=24):
                timings.append({
                    "begin": ics_event_start.isoformat(),
                    "end": ics_event_end.isoformat()
                })
            else:
                # Split into 24-hour intervals
                begin = ics_event_start
                end = ics_event_end
                while begin < end:
                    next_end = min(begin + timedelta(hours=24), end)
                    timings.append({
                        "begin": begin.isoformat(),
                        "end": next_end.isoformat()
                    })
                    begin = next_end

            # Clean up the event description
            description =  unicodedata.normalize('NFKC', str(ics_event.get('DESCRIPTION')) ) if ( 'DESCRIPTION' in ics_event) else "Pas de description"
            name = unicodedata.normalize('NFKC', str(ics_event.get('SUMMARY')) ) if ('SUMMARY' in ics_event ) else "Nom inconnu"
            short_description= description.split("\n")[0][:150] # 200 characters max in short description
            
            # Prepare the OpenAgenda event structure
            new_oa_event = {
                "uid-externe": str(ics_event.get('UID')),
                "slug": slugify(name),
                "title": {"fr": name},
                "description": {"fr": f"{short_description or ''}"},
                "locationTXT": str(ics_event.get('LOCATION')),
                "longDescription": {"fr": description},
                "timings": timings,
                "onlineAccessLink": ics_event.get('url') if ("URL" in ics_event) else None,
                "attendanceMode": 3,  # 1: physical, 2: online, 3: hybrid
            }
            upcoming_ics_events.append(new_oa_event)
    
    return upcoming_ics_events