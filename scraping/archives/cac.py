import pandas as pd
from datetime import datetime
import locale
# Set locale to FR.fr
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

location_uid = 52474812 # CAC

columns = {
    "event-result-title-link":"title",
    "event-result-title-link href":"link",
    "event-result-date":"raw_date",
    "event-result-genre-item":"desc",
    "price 2":"keyword",
    "tm-image src":"img",
    "visually-hidden 2":"long_desc"

}

df = pd.read_csv('scraping/cac.csv', sep=',')

# Rename df columns based on columns dict
df.rename(columns=columns, inplace=True)

# Convert date column to datetime
# Example sam 7 septembre 2024 becomes 2024-09-07
# locale if FR.fr
df['date_start'] = df["raw_date"].apply(lambda x: datetime.strptime(x, "%d %B %Y"))
df['date_end'] = df['date_start']
df['start_date'] = df['date_start'].dt.strftime('%Y-%m-%dT19:00:00+0200')
df['end_date'] = df['date_end'].dt.strftime('%Y-%m-%dT21:00:00+0200')

# df['desc'] = "-"
# df['long_desc'] = ""
df["location_uid"] = location_uid
df["location_name"] = ""
df["keyword"] = "4ASS-" + df["keyword"]
#    0    1       2        3         4        5          6    7     8         9
# title;desc;long_desc;start_date;end_date;location_uid;link;img;keyword;location_name

df = df[['title', 'desc', 'long_desc', 'start_date', 'end_date', 'location_uid', 'link', 'img', 'keyword', 'location_name']]


df.to_csv('csv/cac.csv', index=False, sep=';')