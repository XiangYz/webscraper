import urllib
from urllib.request import urlopen
from bs4 import BeautifulSoup
from selenium import webdriver
from multiprocessing import Process, Pool, Queue
import re
import os
import imghdr
import time
import requests
import pymongo
import sys
import xlwt
import xlrd
from xlutils.copy import copy
import random

    

class pianziweb(object):
    def __init__(self):
        self._catalog_url = "http://pianziweb.com/tel_share/lists/p/"
        self._session = requests.Session()
        self._headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) \
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
        }
        
        self._path_of_file = "../pianziweb.txt"

        


    def start(self):

        cur_url = self._catalog_url + "1.html"
        cnt = 0
        page_cnt = 0

        err_cnt = 0
        while True:
            try:
                cur_page = self._session.get(cur_url, headers = self._headers)
            except:
                time.sleep(1)
                err_cnt += 1
                if err_cnt == 3:
                    break
            if not cur_page:
                continue
            err_cnt = 0
            cur_page.encoding = "utf-8"
            bsobj = BeautifulSoup(cur_page.text, "html.parser")
            
            blacklist = bsobj.findAll("li", {"class":re.compile("^col-xs-12")})

            if not blacklist:
                time.sleep(1)
                continue
            
            for hei in blacklist:
                
                span = hei.find("span", {"class":"fl"})
                if span:
                    ph_num = span.next_sibling.get_text().strip()

                if re.match(r'^[0-9]{8,}$', ph_num):

                    with open(self._path_of_file, 'a') as f:
                        f.write(ph_num + '\n')
                    
                    print(ph_num)
                    cnt = cnt + 1

            page_cnt = page_cnt + 1
            print('\n----------------------------num: ' + str(cnt) + '\n')
            print('\n----------------------------pages: ' + str(page_cnt) + '\n')

            if page_cnt == 1327:
                break 

            cur_url = self._catalog_url + str(page_cnt+1) + ".html"





if __name__ == '__main__':

    pianziweb_spider = pianziweb()
    pianziweb_spider.start()
