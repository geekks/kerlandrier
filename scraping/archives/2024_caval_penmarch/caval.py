import pandas as pd
from datetime import datetime
import locale
# Set locale to FR.fr
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

# location_uid = 26539058 # vauban
location_uid = 1460026 # caval


columns = {
"evenement href":"link",
"evenement src":"img",
"date":"raw_date",
"evenement":"title",
"sub":"keyword",
}

df = pd.read_csv('scraping/2024_caval_penmarch/caval.csv', sep=',')
df.rename(columns=columns, inplace=True)

df['desc'] = "-"
df['long_desc'] = ""
df["location_uid"] = location_uid
df["location_name"] = ""

# Convert date column to datetime
# Example sam 7 septembre 2024 becomes 2024-09-07
# locale if FR.fr
print(df.head(2))
df['date_start'] = df["raw_date"].apply(lambda x: datetime.strptime(x, "%A %d %B %Y"))
df['start_date'] = df['date_start'].dt.strftime('%Y-%m-%dT20:00:00+0200')
df['end_date'] = df['date_start'].dt.strftime('%Y-%m-%dT22:00:00+0200')

#    0    1       2        3         4        5          6    7     8         9
# title;desc;long_desc;start_date;end_date;location_uid;link;img;keyword;location_name

df = df[['title', 'desc', 'long_desc', 'start_date', 'end_date', 'location_uid', 'link', 'img', 'keyword', 'location_name']]


df.to_csv('scraping/2024_caval_penmarch/2024_caval_penmarch.csv', index=False, sep=';')