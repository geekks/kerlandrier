import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import re
import pandas as pd
# Create a session to persist certain parameters across requests
session = requests.Session()

# Set headers to mimic a real browser
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
})

# Optionally set cookies if you have specific ones (e.g., from a previous login)
session.cookies.update({
    'cookielawinfo-checkbox-analytics': 'no',
    'cookielawinfo-checkbox-functional': 'no',
    'cookielawinfo-checkbox-necessary': "yes",
    'CookieLawInfoConsent': "eyJuZWNlc3NhcnkiOnRydWUsImZ1bmN0aW9uYWwiOmZhbHNlLCJhbmFseXRpY3MiOmZhbHNlfQ==",
    'viewed_cookie_policy': "yes"
})

data = []

month_dict = {
    "SEP": [9, 2024],
    "OCT": [10, 2024],
    "NOV": [11, 2024],
    "DÉC": [12, 2024],
    "JAN": [1, 2025],
    "FÉV": [2, 2025],
    "MARS": [3, 2025],
    "AVR": [4, 2025],
    "MAI": [5, 2025],
    "JUIN": [6, 2025],
}

lieu_dict = {
    "Parvis du Théâtre de Cornouaille":33981020,
    "Théâtre de Cornouaille":33981020,
    "Théâtre de Cornouaille - L'Atelier":33981020,
    "Divers lieux":11634941,
    "Le Triskell - Pont-L’Abbé":48680502,
    "Pluguffan - Place Kroaz Ar Bleuñv":84822207,
    "L’Archipel - Fouesnant":16584185,
    "L’Arthémuse - Briec":17422458,
    "Le Katorza":70144942,
    "Médiathèque Alain Gérard - Quimper":50372120,
    "Le Terrain Blanc - MPT de Penhars":25361163,
    "Le Novomax":65307583,
}
TBD_LOCATION_UID = 11634941

#    0    1       2        3         4        5          6    7     8         9
# title;desc;long_desc;start_date;end_date;location_uid;link;img;keyword;location_name
file = "scraping/2024_th_cornouaille_quimper/th_cornouaille.html"
with open(file, 'r', encoding='utf-8') as f:
    file = f.read()
    soup = BeautifulSoup(file, 'html.parser')
    months = list(soup.contents)

    # print(month)
    current_month = None

    for month in months:
        m, shows = [tag for tag in month.contents if not isinstance(tag, str)]
        shows = [show for show in shows.contents if not isinstance(show, str)]
        # print(month_dict[m.attrs['id']])
        m_y = month_dict[m.attrs['id']]
        for show in shows:
            title, desc, long_desc, start_date, end_date, location_uid, link, img, keyword, location_name = [None] * 10
            title = show.find(class_='card-infos').find('h3').text.strip()
            desc = show.find(class_='card-infos').find('p').text.strip()
            long_desc = ""
            
            p_start = show.find(class_='date').text.strip()
            print(p_start)
            regex_time = r'^[A-Z]{2}\s+([0-9]{2})\s+([0-9]{2}\:[0-9]{2})?'
            match_time = re.match(regex_time, p_start)
            regex_days = r'([A-Z]{2})\s+([0-9]{2}).+?([A-Z]{2}).+?([0-9]{2})$'
            match_days = re.findall(r'(?:[A-Z]{2})\s+([0-9]{2})', p_start, flags = re.MULTILINE)
            if match_time and match_time.group(2):
                print(match_time.groups())
                date_start = datetime(int(m_y[1]), int(m_y[0]), int(match_time.group(1)))
                if match_time.group(2):
                    time_start = datetime.strptime(match_time.group(2), '%H:%M').time()
                    date_start = date_start.replace(hour=time_start.hour, minute=time_start.minute)
                else:
                    date_start = date_start.replace(hour=20, minute=0)
                date_end = date_start + timedelta(hours=2)
                start_date = date_start.strftime("%Y-%m-%dT%H:%M:%S+0200")
                end_date = date_end.strftime("%Y-%m-%dT%H:%M:%S+0200")
            elif match_days:
                print(match_days)
                date_start = datetime(int(m_y[1]), int(m_y[0]), int(match_days[0]))
                date_start = date_start.replace(hour=20, minute=0)
                date_end = date_start + timedelta(hours=2)

            else:
                raise ValueError("date not found")

            link = show.find('a').attrs['href']
            img = show.find('picture').find('img').attrs['src']
            discipline = show.find(class_='disciplines')
            type = show.find(class_='type')
            if discipline:
                discipline = [item.text.strip() for item in discipline.contents if item.name == 'p']
                keyword = "/".join(discipline)
            elif type:
                keyword = type.text.strip()
            else:
                keyword = ""
            keyword.replace(r'\r?\n', '')
            location_name = show.find(class_='lieu').text.strip()
            if location_name:
                location_uid = lieu_dict[location_name]
            else:
                location_uid = TBD_LOCATION_UID
            # create a row for a pandas dataframe
            if match_days:
                for day in match_days:
                    date_start = date_start.replace(day=int(day))
                    date_end = date_start + timedelta(hours=2)
                    start_date = date_start.strftime("%Y-%m-%dT%H:%M:%S+0200")
                    end_date = date_end.strftime("%Y-%m-%dT%H:%M:%S+0200")
                    row = [title, desc, long_desc, start_date, end_date, location_uid, link, img, keyword, location_name]
                    data.append(row)
            else:
                row = [title, desc, long_desc, start_date, end_date, location_uid, link, img, keyword, location_name]
                data.append(row)
            # print(row)
        # break

df = pd.DataFrame(data, columns=['title', 'desc', 'long_desc', 'start_date', 'end_date', 'location_uid', 'link', 'img', 'keyword', 'location_name'])
df.to_csv('scraping/2024_th_cornouaille_quimper/th_cornouaille.csv', index=False, sep=';')
