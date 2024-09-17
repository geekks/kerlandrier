"""_summary_
Add Cap Danse events V2 (with time and images)

"""

import sys
import os
import git

# Ajoute le dossier "ressources" au sys.path
git_root = git.Repo(search_parent_directories=True).working_tree_dir
sys.path.insert(0,   os.path.abspath(  os.path.join(  git_root,'resources/python' ) ) )

from utils import *
from scraping_utils import *
from manualHttpRequests import *

import datetime
import re


def get_clubs_logo(club_name):
    sizes=(60,150)
    for size in sizes:
        # headers = {
        # "Content-Type": 'application/json',
        # "nonce": get_nonce(),
        # }
        url = f"https://assets-fr.imgfoot.com/media/cache/" + str(size) + "x" + str(size) + "/club/" + club_name + ".png"
        response = requests.get(url, timeout=10)
        print(i)
        if response.status_code == 200:
            print( url)
            imgUrlName=url.rstrip('/').split("/")[-1]
            imageFullPath = os.path.join("scraping/us_concarneau" , imgUrlName)
            with open(imageFullPath, 'wb') as f:
                        f.write(response.content)


get_clubs_logo("nimes")

# https://assets-fr.imgfoot.com/media/cache/60x60/club/nimes.png
# https://assets-fr.imgfoot.com/media/cache/150x150/club/nimes.png