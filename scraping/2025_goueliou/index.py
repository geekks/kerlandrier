import json
import re
import requests
from bs4 import BeautifulSoup
import gspread
from google.oauth2.service_account import Credentials

import datetime
import locale
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

from festival_bretagne import main as festival_bretagne
from ty_zicos import main as ty_zicos
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
SERVICE_ACCOUNT_FILE = "association-concarneau-3f7ff63d5314.json"
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)
SPREADSHEET_ID = "1Z1x7kJPdJWx5ha9R72SIihwreVV7sF7CnuVIjlArTTE"  # Extracted from your link


source_1 = festival_bretagne()
# print(source_1)

source_2 = ty_zicos()
# print(source_2)


festival_rows = source_1 + source_2
# [title, ville, zipcode, start_date, end_date, url, website_url]
festival_rows_json = [{
    "title": row[0],
    "city": row[1],
    "zipcode": row[2],
    "start_date": row[3],
    "end_date": row[4],
    "url": row[5],
    "website_url": row[6],
    "mois": row[3].split("/")[1],
    "duration": (datetime.datetime.strptime(row[4], "%d/%m/%Y").date() - datetime.datetime.strptime(row[3], "%d/%m/%Y").date()).days + 1} for row in festival_rows]

festival_rows_json.sort(key=lambda x: datetime.datetime.strptime(x['start_date'], "%d/%m/%Y"))

from collections import defaultdict

grouped_by_month = defaultdict(list)
for festival in festival_rows_json:
    grouped_by_month[festival['mois']].append(festival)

with open('goueliou.json', 'w') as outfile:
    json.dump(grouped_by_month, outfile, indent=4, ensure_ascii=False)
# # UPDATE GOOGLE SHEET
# sheet = client.open_by_key(SPREADSHEET_ID).worksheet("FESTIVALS")  # Change to specific sheet name if needed
# print(sheet)
# print(festival_rows)
# sheet.update("A2", festival_rows)