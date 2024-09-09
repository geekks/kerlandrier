
"""_summary_
Functions to help Scrap data from webpages

"""

import csv, os
import requests, requests_cache
from bs4 import BeautifulSoup
import  dateparser, pytz
from urllib.parse import urlparse

getTimeout = 10  # in seconds for Http requests
requests_cache.install_cache('scrap_cache')

def read_csv(file_name):
    """Read a CSV file and return a dictionary of Data objects"""
    data_dict = {}
    with open(file_name, "r", encoding='utf-8') as file:
        reader = csv.DictReader(file)
        data_dict = [ row for row in reader]
    return data_dict


def get_string_from_webpage(url: str, selector: str) -> str:
    """
    Get an info from a string in a webpage
    input @selector in css style. Ex: "#head-event > div > div > div.dates-event > p.bold"
    """
    html_doc = requests.get(url, timeout=getTimeout).text
    parsed_html = BeautifulSoup(html_doc, features="lxml")
    extractedDiv = parsed_html.select_one(selector)
    extractedString = extractedDiv.text if extractedDiv else None
    return extractedString

def download_image_from_webpage(url: str, selector: str , imgTag: str, path:str) -> str:
    """
    Download an image from webpage and css selector\n
    Return: image name\n
    Input:  
    * @url: webpage url\n
    * @selector in css style. Ex: "#head-event > div > picture > img"\n
    * @imgTag: htlm tag containing image url
    """
    eventName=url.rstrip('/').split("/")[-1]
    if not os.path.exists(path):
        os.makedirs(path)
    response = requests.get(url, timeout=getTimeout)
    response.raise_for_status()
    parsed_html = BeautifulSoup(response.text, features="lxml")
    # Using css selector
    img_path = parsed_html.select_one(selector).get(imgTag)
    imgUrlName=img_url.rstrip('/').split("/")[-1]
    if not img_url.startswith('http'):
        img_url = urlparse.urljoin('https://' + urlparse(url).netloc , img_url)
    img_data = requests.get(img_url).content
    
    imageFullPath = os.path.join(path, eventName +"-" + imgUrlName)
    with open(imageFullPath, 'wb') as f:
                f.write(img_data)
    return imageFullPath

def get_iso_date_from_text(stringDate):
    "Convert String to ISO date like 2024-08-20T09:00:00+02:00"
    parsedDate = dateparser.parse(stringDate, languages=["fr"])
    # print("parsedDate: ", parsedDate)
    parisTZ = pytz.timezone("Europe/Paris")
    isoDate = parisTZ.localize(parsedDate).isoformat() if parsedDate else None
    # print("fromisoformat: ", isoDate)
    return isoDate


