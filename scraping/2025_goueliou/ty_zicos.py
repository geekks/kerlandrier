import locale
import re
import requests
from bs4 import BeautifulSoup
import datetime

locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
def main():
    print("--- TY ZICOS ---")
    base_url = "http://www.tyzicos.com"
    root_url = "/concerts-par-festivals/bretagne"

    # GET ALL URLS
    root_response = requests.get(base_url + root_url)
    soup = BeautifulSoup(root_response.text, 'html.parser')
    lis = soup.find_all("li", class_=re.compile("^item"))
    urls = []
    for li in lis:
        href = li.find("a")['href']
        urls.append(base_url + href)

    # GET ALL FESTIVAL DETAILS
    festival_rows = []
    for url in urls:
        festival_response = requests.get(url)
        festival_soup = BeautifulSoup(festival_response.text, 'html.parser')

        dates = festival_soup.find_all("div", class_="date")
        start_date_str = f"{dates[0].find("span", class_="day-num").text} {dates[0].find("span", class_="month").text} {dates[0].find("span", class_="year").text}"
        start_date = datetime.datetime.strptime(start_date_str, "%d %B %Y").strftime('%d/%m/%Y')

        end_date_str = f"{dates[-1].find("span", class_="day-num").text} {dates[-1].find("span", class_="month").text} {dates[-1].find("span", class_="year").text}"
        end_date = datetime.datetime.strptime(end_date_str, "%d %B %Y").strftime('%d/%m/%Y')

        title = festival_soup.find("h1").text

        ville = festival_soup.find("div", class_="ville").find("a").text

        website = festival_soup.find("div", class_="adress").find('a')
        website_url = ''
        if website is not None:
            website_url = website['href']

        zipcode = festival_soup.find("div", class_="adress").find('span').text
        zipcode_pattern = r"(\d{5})"
        match = re.search(zipcode_pattern, zipcode)
        if match:
            zipcode = match.group(1)

        festival_rows.append([title, ville, zipcode, start_date, end_date, url, website_url])
    return festival_rows