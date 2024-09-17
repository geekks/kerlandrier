
"""_summary_
Functions to help Scrap data from webpages

"""

import csv, os
import datetime
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
    Get first string found with css selector in a webpage
    input @selector in css style. Ex: "#head-event > div > div > div.dates-event > p.bold"
    """
    html_doc = requests.get(url, timeout=getTimeout).text
    parsed_html = BeautifulSoup(html_doc, features="lxml")
    extractedDivs = parsed_html.select(selector)
    extractedStrings =""
    for el in extractedDivs:
        extractedStrings += el.text + os.linesep if el.text else  os.linesep
    return extractedStrings

def get_image_from_webpage(url: str, selector: str , imgTag: str, path:str) -> str:
    """
    Get an image from webpage and css selector\n
    Return: 
    * if path is given: the local path of dowloaded image\n
    * else: return image url\n
    Input:  
    * @url: webpage url\n
    * @selector in css style. Ex: "#head-event > div > picture > img"\n
    * @imgTag: htlm tag containing image url\n
    * @path(optionnal): the directory for downloading image
    """
    eventName=url.rstrip('/').split("/")[-1]
    response = requests.get(url, timeout=getTimeout)
    response.raise_for_status()
    parsed_html = BeautifulSoup(response.text, features="lxml")
    # Using css selector
    img_url = parsed_html.select_one(selector).get(imgTag)
    imgName=img_url.rstrip('/').split("/")[-1]
    if not img_url.startswith('http'):
        img_url = urlparse.urljoin('https://' + urlparse(url).netloc , imgName)
    if not path:
        return  img_url
    
    img_data = requests.get(img_url).content
    imageFullPath = os.path.join(path, eventName +"-" + imgName)
    with open(imageFullPath, 'wb') as f:
                f.write(img_data)
    return imageFullPath

def get_datetime_from_text(stringDate:str) -> datetime.datetime:
    "Convert a human readable string to datetime object"
    parsedDate = dateparser.parse(stringDate, languages=["fr"])
    # print("parsedDate: ", parsedDate)
    parisTZ = pytz.timezone("Europe/Paris")
    datetime = parisTZ.localize(parsedDate) if parsedDate else None
    # print("fromisoformat: ", isoDate)
    return datetime


