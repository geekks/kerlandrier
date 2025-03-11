import re
import requests
from bs4 import BeautifulSoup
import gspread
from google.oauth2.service_account import Credentials
import datetime
from festival_bretagne import main as festival_bretagne
from ty_zicos import main as ty_zicos

SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
SERVICE_ACCOUNT_FILE = "association-concarneau-3f7ff63d5314.json"
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)
SPREADSHEET_ID = "1Z1x7kJPdJWx5ha9R72SIihwreVV7sF7CnuVIjlArTTE"  # Extracted from your link


source_1 = festival_bretagne()
print(source_1)

source_2 = ty_zicos()
print(source_2)


festival_rows = source_1 + source_2


# UPDATE GOOGLE SHEET
sheet = client.open_by_key(SPREADSHEET_ID).worksheet("FESTIVALS")  # Change to specific sheet name if needed
print(sheet)
print(festival_rows)
sheet.update("A2", festival_rows)