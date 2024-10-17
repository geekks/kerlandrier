import pandas as pd
from datetime import datetime
import locale
# Set locale to FR.fr
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

location_uid = 33965846 # CC Rosporden
columns = {
"item href":"link",
"adapt-img src":"img",
"dates-evenement":"raw_date",
"item 2":"title",
}

df = pd.read_csv('scraping/ccrospo.csv', sep=',')

# Rename df columns based on columns dict
df.rename(columns=columns, inplace=True)

# Convert date column to datetime
# Example sam 7 septembre 2024 becomes 2024-09-07
# locale if FR.fr
df['date_start'] = df["raw_date"].apply(lambda x: datetime.strptime(x, "%A %d %B %Y"))
df['date_end'] = df['date_start']
df['start_date'] = df['date_start'].dt.strftime('%Y-%m-%dT20:00:00+0200')
df['end_date'] = df['date_end'].dt.strftime('%Y-%m-%dT22:00:00+0200')

# df['title'] = "Quimper Volley vs " + df['title']


df['desc'] = "-"
df['long_desc'] = ""
df["location_uid"] = location_uid
df["location_name"] = ""
df["keyword"] = "4ASS"
#    0    1       2        3         4        5          6    7     8         9
# title;desc;long_desc;start_date;end_date;location_uid;link;img;keyword;location_name

df = df[['title', 'desc', 'long_desc', 'start_date', 'end_date', 'location_uid', 'link', 'img', 'keyword', 'location_name']]


df.to_csv('csv/ccrospo.csv', index=False, sep=';')