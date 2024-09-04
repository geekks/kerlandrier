import pandas as pd
from datetime import datetime
import locale
# Set locale to FR.fr
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

# location_uid = 26539058 # vauban
# location_uid = 1460026 # caval
location_uid = 82722200 # carene
# location_uid = 65307583 # novomax


columns = {
    "rotation href":"link",
    "adapt-img src":"img",
    "titre":"title",
    "jour":"day",
    "mois":"month",
    "annee":"year",
    "genre":"keyword"
}

df = pd.read_csv('scraping/2024_carene_brest/lacarene.csv', sep=',')

# Rename df columns based on columns dict
df.rename(columns=columns, inplace=True)
df = df[~df['keyword'].isin(['Atelier', 'Formation'])]

df['desc'] = "-"
df['long_desc'] = ""
df["location_uid"] = location_uid
df["location_name"] = ""

df['date_start'] = df['day'].astype(str) + ' ' + df['month'].astype(str) + ' 20' + df['year'].astype(str)

df['date_start'] = df['date_start'].apply(lambda x: datetime.strptime(x, "%d %m %Y"))
df['date_end'] = df['date_start'] + pd.Timedelta(hours=2)

df['start_date'] = df['date_start'].dt.strftime('%Y-%m-%dT%H:%M:%S+0200')
df['end_date'] = df['date_end'].dt.strftime('%Y-%m-%dT%H:%M:%S+0200')
# "rotation href","adapt-img src","titre","jour","mois","sep 2","jour 2","mois 2","annee","genre"T20:00:00+0200')

#    0    1       2        3         4        5          6    7     8         9
# title;desc;long_desc;start_date;end_date;location_uid;link;img;keyword;location_name

df = df[['title', 'desc', 'long_desc', 'start_date', 'end_date', 'location_uid', 'link', 'img', 'keyword', 'location_name']]


df.to_csv('scraping/2024_carene_brest/2024_carene_brest.csv', index=False, sep=';')