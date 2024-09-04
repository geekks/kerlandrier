import pandas as pd
from datetime import datetime
import locale
# Set locale to FR.fr
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

# location_uid = 26539058 # vauban
# location_uid = 1460026 # caval
location_uid = 65307583 # novomax


columns = {
    "attachment-carre src":"img",
    "lkbillevtinv href":"link",
    "titartprog":"title",
    "lkevt":"raw_date",
    "titartprog 2":"description",
    "typevt":"keyword",
    "lkbillevt href":"book_link"

}

df = pd.read_csv('scraping/2024_novomax_quimper/novomax.csv', sep=',')
df.rename(columns=columns, inplace=True)

df['desc'] = "-"
df['long_desc'] = ""
df["location_uid"] = location_uid
df["location_name"] = ""

# Convert date column to datetime
# Example sam 7 septembre 2024 becomes 2024-09-07
# locale if FR.fr
print(df.head(2))
df['date_start'] = df["raw_date"].apply(lambda x: x + " - 20:00" if "-" not in x else x)
df['date_start'] = df["date_start"].apply(lambda x: datetime.strptime(x, "%d %B %Y - %H:%M"))
df['date_end'] = df['date_start'] + pd.Timedelta(hours=2) 
df['start_date'] = df['date_start'].dt.strftime('%Y-%m-%dT%H:%M:%S+0200')
df['end_date'] = df['date_end'].dt.strftime('%Y-%m-%dT%H:%M:%S+0200')

#    0    1       2        3         4        5          6    7     8         9
# title;desc;long_desc;start_date;end_date;location_uid;link;img;keyword;location_name

df = df[['title', 'desc', 'long_desc', 'start_date', 'end_date', 'location_uid', 'link', 'img', 'keyword', 'location_name']]


df.to_csv('scraping/2024_novomax_quimper/2024_novomax_quimper.csv', index=False, sep=';')