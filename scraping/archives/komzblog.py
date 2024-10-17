import pandas as pd
from datetime import datetime
import locale
# Set locale to FR.fr
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

location_uid = 20623325 # Halle Sport Ergué Armel

columns = {
    "map-date":"raw_date","titre_francais":"title","map-liste-adresse-val":"location_name"

}

locations = {
    "Ti Liamm, Rue Pierre Jacob dit Talcoat, Clohars-Carnoët":"60443775",
    "Chateau de Kerambleiz, Quimper":"94371908",
    "Salle Mirabeau : rue Louis Arretche, Rennes":"49827169",
    "Ti ar Vro - L'Ôté, 138 rue du Légué, Saint-Brieuc":"56953730",
    "8 contour Saint-Aubin, Rennes":"63946502",
    "40 Boulevard Clemenceau, Saint-Brieuc":"37610547",
    "3 esplanade Famille Gabaï, 29000 Quimper ·, quimper":"63609791",
    "101 Croix Luc, Bannalec":"81980866"
}

df = pd.read_csv('scraping/komzblog.csv', sep=',')

# Rename df columns based on columns dict
df.rename(columns=columns, inplace=True)

# Convert date column to datetime
# Example sam 7 septembre 2024 becomes 2024-09-07
# locale if FR.fr
df['date_start'] = df["raw_date"].apply(lambda x: datetime.strptime(x, "%d/%m/%Y"))
df['date_end'] = df['date_start']
df['start_date'] = df['date_start'].dt.strftime('%Y-%m-%dT19:00:00+0200')
df['end_date'] = df['date_end'].dt.strftime('%Y-%m-%dT20:00:00+0200')

# df['title'] = "Quimper Volley vs " + df['title']


df['desc'] = "-"
df['long_desc'] = ""
df["location_uid"] = df["location_name"].apply(lambda x: locations[x])
df["location_name"] = ""
df["keyword"] = "Komz-Brezhoneg"
df["link"] = "https://www.komzblog.bzh/evenements/"
df["img"] = "https://www.komzblog.bzh/wp-content/themes/roquette-twig/static/images/logo.png"
#    0    1       2        3         4        5          6    7     8         9
# title;desc;long_desc;start_date;end_date;location_uid;link;img;keyword;location_name

df = df[['title', 'desc', 'long_desc', 'start_date', 'end_date', 'location_uid', 'link', 'img', 'keyword', 'location_name']]


df.to_csv('csv/komzblog.csv', index=False, sep=';')