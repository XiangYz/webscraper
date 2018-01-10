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

    

class pz748(object):
    def __init__(self):
        self._catalog_url = "http://pz748.net"
        self._session = requests.Session()
        self._headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) \
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
        }
        
        self._path_of_file = "../pz748.txt"

        


    def start(self):

        cur_url = self._catalog_url + "/dh/"
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
            
            ul = bsobj.find("ul", {"class":"news_list"})
            if not ul:
                time.sleep(1)
                continue
            blacklist = ul.findAll("li")
            if not blacklist:
                time.sleep(1)
                continue
            for hei in blacklist:
                
                strong = hei.find("strong")
                if strong:
                    ph_num = strong.get_text()

                if re.match(r'^[0-9]{5,}$', ph_num):

                    with open(self._path_of_file, 'a') as f:
                        f.write(ph_num + '\n')
                    
                    print(ph_num)
                    cnt = cnt + 1

            page_cnt = page_cnt + 1
            print('\n----------------------------num: ' + str(cnt) + '\n')
            print('\n----------------------------pages: ' + str(page_cnt) + '\n')

            next_page = bsobj.findAll("a", text=re.compile("下一页"))
            if not next_page:
                break
            cur_url = self._catalog_url + next_page[0].attrs['href']





if __name__ == '__main__':

    pz748_spider = pz748()
    pz748_spider.start()
