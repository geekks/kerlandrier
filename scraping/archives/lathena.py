import pandas as pd
from datetime import datetime
import re
import locale
# Set locale to FR.fr
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

# location_uid = 75450604 # Run ar
# location_uid = 62258283 # Hydrophone
# location_uid = 69566574 # Th Lorient
location_uid = 91086232 # L'Athéna

columns = {
    "card__link href":"link",
    "a42-ac-replace-img src":"img",
    "card__date_day":"raw_day",
    "card__date_month":"raw_month",
    "card__category":"keyword",
    "card__title":"title",
    "card__description":"desc"

}


df = pd.read_csv('scraping/lathena.csv', sep=',')

# Rename df columns based on columns dict
df.rename(columns=columns, inplace=True)

# df.replace(to_replace=r'\n', value=' ', regex=True, inplace=True)

df['raw_date'] = df['raw_day'].astype(str) + ' ' + df['raw_month'].astype(str) + ' 2024'
df['date_start'] = df['raw_date'].apply(lambda x: datetime.strptime(x, '%d %B %Y'))

df['start_date'] = df['date_start'].dt.strftime('%Y-%m-%dT20:00:00+0200')
df['end_date'] = df['date_start'].dt.strftime('%Y-%m-%dT22:00:00+0200')

# df['desc'] = "-"
df['long_desc'] = ""
df["location_uid"] = location_uid
df["location_name"] = ""

print(df.head(2))
#    0    1       2        3         4        5          6    7     8         9
# title;desc;long_desc;start_date;end_date;location_uid;link;img;keyword;location_name

df = df[['title', 'desc', 'long_desc', 'start_date', 'end_date', 'location_uid', 'link', 'img', 'keyword', 'location_name']]


df.to_csv('scraping/2024_lathena.csv', index=False, sep=';')