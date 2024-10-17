import pandas as pd
from datetime import datetime
import locale
# Set locale to FR.fr
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

location_uid = 20623325 # Halle Sport Ergué Armel

columns = {
    "eventRowLink href":"link",
    "event__time":"raw_date",
    "event__participant":"vs",
    "event__logo src 2":"img",
    "event__participant 2":"title",
}

df = pd.read_csv('scraping/quimper_volley_ligue_a_feminine.csv', sep=',')

# Rename df columns based on columns dict
df.rename(columns=columns, inplace=True)

df = df[df["vs"] == "Quimper F"]

# Convert date column to datetime
# Example sam 7 septembre 2024 becomes 2024-09-07
# locale if FR.fr
df['date_start'] = df["raw_date"].apply(lambda x: datetime.strptime(x, "%d.%m.%Y %H:%M"))
df['date_end'] = df['date_start']
df['start_date'] = df['date_start'].dt.strftime('%Y-%m-%dT20:00:00+0200')
df['end_date'] = df['date_end'].dt.strftime('%Y-%m-%dT22:00:00+0200')

# Prefix title with "Bélier"
df['title'] = "Quimper Volley vs " + df['title']


df['desc'] = "-"
df['long_desc'] = ""
df["location_uid"] = location_uid
df["location_name"] = ""
df["keyword"] = "Volley"
#    0    1       2        3         4        5          6    7     8         9
# title;desc;long_desc;start_date;end_date;location_uid;link;img;keyword;location_name

df = df[['title', 'desc', 'long_desc', 'start_date', 'end_date', 'location_uid', 'link', 'img', 'keyword', 'location_name']]


df.to_csv('csv/quimper_volley_ligue_a_feminine.csv', index=False, sep=';')