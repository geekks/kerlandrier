import pandas as pd
from datetime import datetime
import locale
# Set locale to FR.fr
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

location_uid = 52474812
# location_uid = 26539058 # vauban
# location_uid = 1460026 # caval
# location_uid = 82722200 # carene
# location_uid = 65307583 # novomax


columns = {
    "rte": "title",
    "rte 2": "long_desc",
    "rte 3": "long_desc",
    "table-responsive": "raw_date_location",
    "table-responsive 2": "desc",
    "col-xs-12 src": "img",
}

locations = {
"MÉDIATHÈQUE D’ELLIANT": "64345896",
"MÉDIATHÈQUE DE TOURC’H": "87389099",
"MUSÉE DE PONT-AVEN": "52873907",
"MÉDIATHÈQUE DE NÉVEZ": "31001182",
"MÉDIATHÈQUE DE MELGVEN": "31482342",
"MUSÉE DE LA PÊCHE": "58508752",
"MÉDIATHÈQUE DE ROSPORDEN": "56999968",
"MÉDIATHÈQUE DE CONCARNEAU": "9527696",
"CINÉVILLE": "24412066",
"MÉDIATHÈQUE DE SAINT-YVI": "55624267",
"MJC LE STÉRENN DE TRÉGUNC": "89326663",
"MÉDIATHÈQUE DE PONT-AVEN": "6135974",
}

df = pd.read_csv('scraping/cca_mois_film_document.csv', sep=',')

# Rename df columns based on columns dict
df.rename(columns=columns, inplace=True)

# split raw_date_location based on |
df['raw_date'] = df['raw_date_location'].str.split('│').str[0]
df['raw_date'] = df['raw_date'].apply(lambda x: x + '2024')    
# get raw_date
# get raw_time
df['raw_time'] = df['raw_date_location'].str.split('│').str[1]
df['raw_date_time'] = df['raw_date'] + df['raw_time']
# convert to start_date and end_date
# get location_name
df['location_name'] = df['raw_date_location'].str.split('│').str[2]
# convert location_name to location_uid

# Convert date column to datetime
# Example sam 7 septembre 2024 becomes 2024-09-07
# locale if FR.fr
df['date_start'] = df["raw_date_time"].apply(lambda x: datetime.strptime(x.strip(), "%A %d %B %Y %H:%M"))
df['date_end'] = df['date_start'] + pd.Timedelta(hours=2) 
df['start_date'] = df['date_start'].dt.strftime('%Y-%m-%dT%H:%M:%S+0200')
df['end_date'] = df['date_end'].dt.strftime('%Y-%m-%dT%H:%M:%S+0200')

# df['desc'] = df['desc_2'] + ' ' + df['desc_1']
# df['long_desc'] = ""
df["location_uid"] = df["location_name"].apply(lambda x: locations[x.strip()])
# df["location_name"] = ""
df["link"] = "https://www.cca.bzh/evenements/mois-du-film-documentaire/"
df["keyword"] = "CCA-Le-Mois-Du-Film-Docu-FR3"

print(df.head(2))

#    0    1       2        3         4        5          6    7     8         9
# title;desc;long_desc;start_date;end_date;location_uid;link;img;keyword;location_name

df = df[['title', 'desc', 'long_desc', 'start_date', 'end_date', 'location_uid', 'link', 'img', 'keyword', 'location_name']]


df.to_csv('csv/2024_cca_mois_film_docu.csv', index=False, sep=';')