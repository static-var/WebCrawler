from bs4 import BeautifulSoup
import os
import urllib
import urllib.parse
from tabulate import tabulate
import requests
from urllib.parse import urlsplit

# returns all the unique values from the list
def giveSets(lists):
    return set(lists)

# return the name of the website with domain
def domainName(DName):
    domain = "{0.scheme}://{0.netloc}/".format(urlsplit(DName))

def crawl(Name):
    try:
        packets = requests.get(Name)
    except TimeoutError:
        print("Connection Time Out")
    except requests.exceptions.ConnectionError:
        print("Connection Time Out")

    SC = packets.text
    soup = BeautifulSoup(SC,"html.parser")
    links = []
    for i in soup.find_all('a',href=True):
        links.append(i['href'])

