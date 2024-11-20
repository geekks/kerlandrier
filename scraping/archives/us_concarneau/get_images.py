"""_summary_
Get logo from KK opponents

"""

import sys
import os
import git

# Ajoute le dossier "ressources" au sys.path
git_root = git.Repo(search_parent_directories=True).working_tree_dir
sys.path.insert(0,   os.path.abspath(  os.path.join(  git_root,'resources/python' ) ) )

from utils import *
from scraping_utils import *
from HttpRequests import *
from slugify import slugify

def get_club_logo(club_name):
    sizes=(60,150)
    for size in sizes:
        url = f"https://assets-fr.imgfoot.com/media/cache/" + str(size) + "x" + str(size) + "/club/" + club_name + ".png"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print( url)
            imgUrlName=url.rstrip('/').split("/")[-1]
            imageFullPath = os.path.join(git_root,"scraping/us_concarneau/images" , str(size) + "x" + str(size) + "-" + imgUrlName)
            with open(imageFullPath, 'wb') as f:
                        f.write(response.content)

match_data = read_csv("scraping/us_concarneau/2024_25_matchs_footmercato.csv")
print_well_json(match_data)
for entry in match_data:
    get_club_logo(slugify(entry.get('matchTeam__name 2')))
    get_club_logo('concarneau')

# https://assets-fr.imgfoot.com/media/cache/60x60/club/nimes.png
# https://assets-fr.imgfoot.com/media/cache/150x150/club/nimes.png