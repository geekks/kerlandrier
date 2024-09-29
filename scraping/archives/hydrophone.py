import pandas as pd
from datetime import datetime
import re
import locale
# Set locale to FR.fr
# locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

# location_uid = 75450604 # Run ar
location_uid = 62258283 # Hydrophone
# location_uid = 69566574 # Th Lorient

columns = {
    "agenda-item href":"link",
    "img-fluid src":"img",
    "mb-0":"raw_date",
    "d-block":"keyword",
    "mb-0 3":"title",
}

def convert_date(stringDate:str) -> datetime:
    # Remove all \n
    stringDate = stringDate.replace('\n', ' ')
    stringDate = stringDate.replace('/', ' ')
    stringDate = stringDate.replace('\xa0', '')
    stringDate = re.sub(r'(?:^[^0-9]+)(\d.*)$', r'\1', stringDate)
    stringDate = "2024 " + stringDate
    if stringDate.endswith('h'):
        stringDate = datetime.strptime(stringDate, "%Y %d %b %Hh")
    else:
        stringDate = datetime.strptime(stringDate, "%Y %d %b %Hh%M")

    return stringDate



df = pd.read_csv('scraping/hydrophone.csv', sep=',')

# Rename df columns based on columns dict
df.rename(columns=columns, inplace=True)

df.replace(to_replace=r'\n', value=' ', regex=True, inplace=True)

df['date_start'] = df['raw_date'].apply(convert_date)
df['date_end'] = df['date_start'] + pd.Timedelta(hours=2) 

df['start_date'] = df['date_start'].dt.strftime('%Y-%m-%dT%H:%M:%S+0200')
df['end_date'] = df['date_end'].dt.strftime('%Y-%m-%dT%H:%M:%S+0200')

df['desc'] = "-"
df['long_desc'] = ""
df["location_uid"] = location_uid
df["location_name"] = ""

print(df.head(2))
#    0    1       2        3         4        5          6    7     8         9
# title;desc;long_desc;start_date;end_date;location_uid;link;img;keyword;location_name

df = df[['title', 'desc', 'long_desc', 'start_date', 'end_date', 'location_uid', 'link', 'img', 'keyword', 'location_name']]


df.to_csv('scraping/2024_hydrophone.csv', index=False, sep=';')