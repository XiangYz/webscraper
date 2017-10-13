import urllib
from urllib.request import urlopen
from bs4 import BeautifulSoup
from selenium import webdriver
import re
import os
import imghdr
import time
import requests


class Douban(object):
    def __init__(self, start_url):
        self.start_url = start_url
        self.session = requests.Session()
        self.headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        }
    
    def crawl_one_page(self, page_url):
        book = {};
        page = self.session.get(page_url, headers = self.headers)
        bsobj = BeautifulSoup(page.content, "html.parser")
        book['name'] = bsobj.find("span", {"property":"v:itemreviewed"}).get_text()
        infoobj = bsobj.find("div", {"id":"info"})
        #
        author = infoobj.find(text=re.compile("作者")).next_sibling.next_sibling.get_text()
        print(author)


        # 
        infolist = infoobj.findAll("span", {"class":"pl"})
        book['author'] = infolist[0].next_sibling.next_sibling.get_text().strip().replace("\n", "")
        book['press'] = infolist[1].next_sibling.string.strip().replace("\n", "")
        book['origin_name'] = infolist[2].next_sibling.string.strip().replace("\n", "")
        book['date'] = infolist[4].next_sibling.string.strip().replace("\n", "")
        book['pages'] = infolist[5].next_sibling.string.strip().replace("\n", "")
        book['price'] = infolist[6].next_sibling.string.strip().replace("\n", "")
        book['layout'] = infolist[7].next_sibling.string.strip().replace("\n", "")
        book['series'] = infolist[8].next_sibling.next_sibling.string.strip().replace("\n", "")
        book['ISBN'] = infolist[9].next_sibling.string.strip().replace("\n", "")
        #print(book)

        return book




start_url = "https://book.douban.com/subject/1477390/"
douban_spider = Douban(start_url)
douban_spider.crawl_one_page(start_url)
