import pandas as pd
from datetime import datetime
import locale
# Set locale to FR.fr
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

location_uid = 17672064 # centre ville douarn


columns = {
    "card__link href":"link",
    "a42-ac-replace-img src":"img",
    "card__date_day":"raw_day_start",
    "card__date_month":"raw_month_start",
    "card__date href":"raw_year_start",
    "card__date_day 2":"raw_day_end",
    "card__date_month 2":"raw_month_end",
    "raw_year_end":"raw_year_end",
    "card__title":"title",
    "card__description":"desc"

}

def compute_end_date(x):
    if x != 'nan nan nan':
        return datetime.strptime(x, "%d %B %Y")

df = pd.read_csv('scraping/douarnenez.csv', sep=',', dtype=str)

# Rename df columns based on columns dict
df.rename(columns=columns, inplace=True)

df["raw_date_start"] = df['raw_day_start'].astype(str) + ' ' + df['raw_month_start'].astype(str) + ' ' + df['raw_year_start'].astype(str)
df["raw_date_end"] = df['raw_day_end'].astype(str) + ' ' + df['raw_month_end'].astype(str) + ' ' + df['raw_year_end'].astype(str)


df['date_start'] = df["raw_date_start"].apply(lambda x: datetime.strptime(x, "%d %B %Y"))
df['date_end'] = df["date_start"]
print(df.head(2))
df['date_end'] = df['raw_date_end'].apply(compute_end_date)
df['start_date'] = df['date_start'].dt.strftime('%Y-%m-%dT%H:%M:%S+0200')
df['end_date'] = df['date_end'].dt.strftime('%Y-%m-%dT%H:%M:%S+0200')

df['desc'] = df['desc'].fillna('-')
df['long_desc'] = ""
df["location_uid"] = location_uid
df["location_name"] = ""
df["keyword"] = ""

#    0    1       2        3         4        5          6    7     8         9
# title;desc;long_desc;start_date;end_date;location_uid;link;img;keyword;location_name

df = df[['title', 'desc', 'long_desc', 'start_date', 'end_date', 'location_uid', 'link', 'img', 'keyword', 'location_name']]


df.to_csv('scraping/2024_douarnenez.csv', index=False, sep=';')