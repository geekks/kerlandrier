import pandas as pd
from datetime import datetime
import re
import locale
# Set locale to FR.fr
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

location_uid = 69566574 # Th Lorient

columns = {
    "spectacle href":"link",
    "img-responsive src":"img",
    "hover-box":"keyword",
    "hover-box 2":"raw_date",
    "hover-box 3":"desc",
    "info":"title",
}


df = pd.read_csv('scraping/theatredelorient.csv', sep=',')

# Rename df columns based on columns dict
df.rename(columns=columns, inplace=True)

# df.replace(to_replace=r'\n', value=' ', regex=True, inplace=True)

df['date_start'] = df['raw_date'].apply(lambda x: datetime.strptime(x, '%d/%m/%Y'))

df['start_date'] = df['date_start'].dt.strftime('%Y-%m-%dT20:00:00+0200')
df['end_date'] = df['date_start'].dt.strftime('%Y-%m-%dT22:00:00+0200')

#default value for desc to - if null
df['desc'] = df['desc'].fillna('-')
df['long_desc'] = ""
df["location_uid"] = location_uid
df["location_name"] = ""

print(df.head(2))
#    0    1       2        3         4        5          6    7     8         9
# title;desc;long_desc;start_date;end_date;location_uid;link;img;keyword;location_name

df = df[['title', 'desc', 'long_desc', 'start_date', 'end_date', 'location_uid', 'link', 'img', 'keyword', 'location_name']]


df.to_csv('scraping/2024_theatredelorient.csv', index=False, sep=';')