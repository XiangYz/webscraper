from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import random
import datetime


pages = set()

def getLinks(articleUrl):
    global pages
    html = urlopen("http://en.wikipedia.org" + articleUrl)
    bsObj = BeautifulSoup(html, "html.parser")

    try:
        #print(bsObj.h1.get_text())
        #print(bsObj.find(id = "mw-content-text").findAll("p")[0])
        #print(bsObj.find(id = "ca-edit").find("span").find("a").attrs['href'])
        pass
    except AttributeError:
        print("This page is missing something! No worries though!")

    for link in bsObj.findAll("a", href = re.compile("^(/wiki/)")):
        if 'href' in link.attrs:
            if link.attrs['href'] not in pages:
                newPage = link.attrs['href']
                print("---------------\n" + newPage)
                pages.add(newPage)
                getLinks(newPage)

getLinks("")