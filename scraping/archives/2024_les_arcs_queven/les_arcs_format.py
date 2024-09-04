# Date parsing fuckedup - Didn't manage to create proper date object while parsing date string

#    0    1       2        3         4        5          6    7     8         9
# title;desc;long_desc;start_date;end_date;location_uid;link;img;keyword;location_name
import pandas as pd
from datetime import datetime

columns = {
"agenda_listing_spectacle_hover href":"link",
"agenda_listing_spectacle_image src":"img",
"agenda_listing_spectacle_title":"title",
"agenda_listing_spectacle_inner_top_style":"keyword",
"agenda_listing_spectacle_inner_top_date_inner_left":"date",
"agenda_listing_spectacle_inner_top_date_inner_left 2":"year",
"agenda_listing_spectacle_inner_top_date_inner_right":"time",
"agenda_listing_spectacle_title 2":"desc",
"agenda_listing_spectacle_inner_partie":"long_desc"
}

LOCATION_UID = 51319332

# Mapping of French month abbreviations to English
french_to_english_months = {
    'jan': 'Jan', 'fév': 'Feb', 'mars': 'Mar', 'avr': 'Apr', 
    'mai': 'May', 'juin': 'Jun', 'juil': 'Jul', 'août': 'Aug', 
    'sept': 'Sep', 'oct': 'Oct', 'nov': 'Nov', 'déc': 'Dec'
}

# Function to parse the date and add the default year
def parse_french_date(date_str, default_year = 2024):
    # Split the date string to extract the day and the French month abbreviation
    parts = date_str.split()
    day = parts[1]
    month = parts[2]
    
    # Convert the French month abbreviation to English
    month_eng = french_to_english_months.get(month.lower(), month)
    
    # Combine the day, English month, and default year
    date_obj = datetime.strptime(f"{day} {month_eng} {default_year}", '%d %b %Y')
    
    # Return the date in the format 'dd/mm/yyyy'
    return date_obj.strftime('%Y%m%d')

def convert_time_format(time_str):
    # Check if the time string includes minutes
    if 'h' in time_str:
        # Split the string into hour and minute
        parts = time_str.split('h')
        hour = parts[0]
        minute = parts[1] if len(parts) > 1 else '00'  # Default to '00' if no minutes are provided
        # Return formatted time string
        return f"{hour.zfill(2)}:{minute.zfill(2)}:00"
    return time_str

df = pd.read_csv('scraping/2024_les_arcs_queven/lesarcs.csv', sep=',')
# Rename df columns based on columns dict
df.rename(columns=columns, inplace=True)
df['location_uid'] = LOCATION_UID
df['location_name'] = ''

df['date_start'] = df['date'].apply(lambda x: parse_french_date(x))
df['date_start'] = pd.to_datetime(df['date_start'])
# # replace year in date_start by value in column year
# df['date_start'] = df['date_start'].apply(lambda x: x.replace(year=int(df['year'].iloc[0])))
df['time_start'] = df['time'].apply(lambda x: convert_time_format(x))
df['datetime_start'] = pd.to_datetime(df['date_start'].astype(str) + ' ' + df['time_start'].astype(str))
df['start_date'] = df['datetime_start'].dt.strftime('%Y-%m-%dT%H:%M:%s+0200')

df['date_end'] = df['date'].apply(lambda x: parse_french_date(x))
df['time_end'] = df['time'].apply(lambda x: convert_time_format(x))
df['datetime_end'] = pd.to_datetime(df['date_end'].astype(str) + ' ' + df['time_end'].astype(str), dayfirst=True)
df['end_date'] = df['datetime_end'].dt.strftime('%Y-%m-%dT%H:%M:%s+0200')

# If desc null replace by -
df['desc'] = df['desc'].fillna('-')

# Keep only the relevant columns in this order
# # title;desc;long_desc;start_date;end_date;location_uid;link;img;keyword;location_name
df = df[['title', 'desc', 'long_desc', 'start_date', 'end_date', 'location_uid', 'link', 'img', 'keyword', 'location_name']]

df.to_csv('scraping/2024_les_arcs_queven/lesarcs_format.csv', index=False, sep=';')
print(df.head(10))
