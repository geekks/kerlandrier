"""_summary_"""

import sys,os
from git import Repo

# Ajoute le dossier "ressources" au sys.path
git_root = Repo(search_parent_directories=True).working_tree_dir
sys.path.insert(0,   os.path.abspath(  os.path.join(  git_root,'resources/python' ) ) )

from InquirerPy import prompt, inquirer
from InquirerPy.validator import PathValidator
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
import shutil, csv
import pandas as pd


from utils import *
from HttpRequests import *

home_path = git_root if git_root else "~/"
csv_path = inquirer.filepath(
    message="Enter csv file path containing events wihtout their OA UID",
    default= home_path + "/scraping/archives/2024_archipel_fouesnant/archipel_format.csv",
    validate= PathValidator(is_file=True, message="Input is not a file")
).execute()


# create backup
shutil.copyfile( csv_path, csv_path + ".bak", follow_symlinks=True)

# Load CSV data to Dict
try:
    with open(csv_path, "r", encoding='utf-8') as file:
        dictreader = csv.DictReader(file, delimiter=';')
        headers = dictreader.fieldnames
        data_dict = [ row for row in dictreader]
except csv.Error as e:
    print(f"Erreur lors de la lecture du fichier CSV : {e}")
except Exception as e:
    print(f"Une erreur s'est produite : {e}")
    
# Choose event name column and validate with first 3 rows
eventname = inquirer.select(
    message= "select a column containing the event name (to search it in OA events)",
    choices= headers
).execute()

if eventname:
    validation = inquirer.confirm(
    message="Is these data OK for looking for an event Title ? " + str( [entry[eventname] for entry in data_dict[:3] ] ) + " ...",
    default= True,
    ).execute()

if (not validation) : exit(0)

for row in data_dict:
    event_uid = get_uid_from_name_date(row[eventname], row['start_date'].split("T")[0])
    existing_event=get_events(params={"uid": event_uid})['events'][0] if event_uid else None
    existing_event_title = existing_event.get('title', {}).get('fr', "") if existing_event else "NOT FOUND"
    print("event_name: " + row[eventname] + "---- existing event name----- " + str(existing_event_title))