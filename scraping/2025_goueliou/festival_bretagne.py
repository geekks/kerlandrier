import re
import requests
from bs4 import BeautifulSoup
import datetime


def main():
    print("--- FESTIVAL BRETAGNE ---")
    base_url = "https://www.festival-bretagne.fr"
    root_response = requests.get(base_url)
    soup = BeautifulSoup(root_response.text, 'html.parser')
    tables = soup.find_all("div", class_="table-festival")

    urls = []
    for table in tables:
        cells = table.find_all("div", class_="cel1-festival")
        for cell in cells:
            href = cell.find("a")['href']
            urls.append(href)

    festival_rows = []
    for url in urls:
        if url == "https://www.festival-bretagne.fr/festival/lirreductible-festival/":
            continue
        festival_response = requests.get(url)
        festival_soup = BeautifulSoup(festival_response.text, 'html.parser')

        dates = festival_soup.find("h3").find("p").text
        date_pattern = r"Du (\d{2}/\d{2}/\d{4}) au (\d{2}/\d{2}/\d{4})"
        match = re.search(date_pattern, dates)
        if match:
            start_date = match.group(1)
            end_date = match.group(2)

        title = festival_soup.find("h1").text

        ville = festival_soup.find("ins")['data-address']

        website = festival_soup.find("h2", class_="titre").findNext("p").find("a")
        website_url = ''
        if website is not None:
            website_url = website['href']

        zipcode = ''
        if ville is not None:
            zipcode_pattern = r"(\d{5})"
            match = re.search(zipcode_pattern, ville)
            if match:
                zipcode = match.group(1)

        festival_rows.append([title, ville, zipcode, start_date, end_date, url, website_url])
    
    return festival_rows