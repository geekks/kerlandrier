import pandas as pd
import locale
from datetime import datetime

locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
DEFAULT_TIME_START = "20:00:00"
DEFAULT_TIME_END = "22:00:00"

columns = {"grid-item href": "link","dates":"raw_dates","cat-ev":"keyword","contenu":"title","contenu 2":"desc","buy-see href 2":"book_link"}

ignored_keywords = ["Exposition", "Rencontre", "Club", "Les animations pour les tout-petits", "Conversation", "Atelier"]

df = pd.read_csv('scraping/2024_archipel_fouesnant/archipel.csv', sep=',')

# Rename df columns based on columns dict
df.rename(columns=columns, inplace=True)


df = df[~df['keyword'].isin(ignored_keywords)]
df = df[~df['raw_dates'].str.contains("Du")]

# Convert date column to datetime
# Example samedi 7 septembre 2024 becomes 2024-09-07
df['date_start'] = df["raw_dates"].apply(lambda x: datetime.strptime(x, "%A %d %B %Y"))
df["start_date"] = df["date_start"].dt.strftime(f"%Y-%m-%dT{DEFAULT_TIME_START}+0200")
df["end_date"] = df["date_start"].dt.strftime(f"%Y-%m-%dT{DEFAULT_TIME_END}+0200")

df['long_desc'] = ""
df['img'] = ""
df['location_name'] = ""
df['location_uid'] = 16584185
#    0    1       2        3         4        5          6    7     8         9
# title;desc;long_desc;start_date;end_date;location_uid;link;img;keyword;location_name

df = df[['title', 'desc', 'long_desc', 'start_date', 'end_date', 'location_uid', 'link', 'img', 'keyword', 'location_name','book_link']]


print(df)
df.to_csv('scraping/2024_archipel_fouesnant/archipel_format.csv', index=False, sep=';')