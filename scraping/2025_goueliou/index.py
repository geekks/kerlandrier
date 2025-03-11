import re
import requests
from bs4 import BeautifulSoup
import gspread
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
SERVICE_ACCOUNT_FILE = "association-concarneau-3f7ff63d5314.json"
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)
SPREADSHEET_ID = "1Z1x7kJPdJWx5ha9R72SIihwreVV7sF7CnuVIjlArTTE"  # Extracted from your link


base_url = "http://www.tyzicos.com"
root_url = "/concerts-par-festivals/bretagne"

# GET ALL URSLS
root_response = requests.get(base_url + root_url)
soup = BeautifulSoup(root_response.text, 'html.parser')
lis = soup.find_all("li", class_=re.compile("^item"))
urls = []
for li in lis:
    href = li.find("a")['href']
    urls.append(base_url + href)
print(urls)



# GET ALL FESTIVAL DETAILS
festival_rows = []
for url in urls:
    print(url)
    festival_response = requests.get(url)
    festival_soup = BeautifulSoup(festival_response.text, 'html.parser')

    dates = festival_soup.find_all("div", class_="date")
    start_date = f"{dates[0].find("span", class_="day-num").text} {dates[0].find("span", class_="month").text} {dates[0].find("span", class_="year").text}"
    end_date = f"{dates[-1].find("span", class_="day-num").text} {dates[-1].find("span", class_="month").text} {dates[-1].find("span", class_="year").text}"

    title = festival_soup.find("h1").text

    ville = festival_soup.find("div", class_="ville").find("a").text

    website = festival_soup.find("div", class_="adress").find('a')
    website_url = ''
    if website is not None:
        website_url = website['href']

    festival_rows.append([title, ville, start_date, end_date, url, website_url])


# UPDATE GOOGLE SHEET
sheet = client.open_by_key(SPREADSHEET_ID).worksheet("FESTIVALS")  # Change to specific sheet name if needed
print(sheet)
print(festival_rows)
sheet.update("A2", festival_rows)