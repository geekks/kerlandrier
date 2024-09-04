import pandas as pd
from datetime import datetime
import locale
# Set locale to FR.fr
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

location_uid = 26539058 # vauban


columns = {
"ic-text-decoration-none href":"link",
"ic-day":"day",
"ic-month":"month",
"ic-year":"year",
"ic-time":"time",
"ic-text-decoration-none":"title",
"descshort":"long_desc",
}

df = pd.read_csv('scraping/2024_vauban_brest/vauban.csv', sep=',')
df.rename(columns=columns, inplace=True)

df['desc'] = "-"
# df['long_desc'] = ""
df['img'] = ""
df['keyword'] = "Vauban"

df["location_uid"] = location_uid
df["location_name"] = ""

# Convert date column to datetime
# Example sam 7 septembre 2024 becomes 2024-09-07
# locale if FR.fr
df['date_start'] = df["year"].astype(str) + "-" + df["month"].astype(str) + "-" + df["day"].astype(str) + " " + df['time']
print(df.head(2))
df['date_start'] = df['date_start'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M'))
df['date_end'] = df['date_start'] + pd.Timedelta(hours=2)
df['start_date'] = df['date_start'].dt.strftime('%Y-%m-%dT%H:%M:%S+0200')
df['end_date'] = df['date_end'].dt.strftime('%Y-%m-%dT%H:%M:%S+0200')

#    0    1       2        3         4        5          6    7     8         9
# title;desc;long_desc;start_date;end_date;location_uid;link;img;keyword;location_name

df = df[['title', 'desc', 'long_desc', 'start_date', 'end_date', 'location_uid', 'link', 'img', 'keyword', 'location_name']]


df.to_csv('scraping/2024_vauban_brest/2024_vauban_brest.csv', index=False, sep=';')