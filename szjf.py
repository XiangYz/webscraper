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




class szjf(object):
    def __init__(self):
        self._catalog_url = "http://sz.szhk.com/2014/06/06/282876982427332.html"
        self._session = requests.Session()
        self._headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) \
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
        }
        
        self._path_of_file = "../szjf.txt"

        


    def start(self):

        

        cur_url = self._catalog_url
        cnt = 0
        

        # if os.path.exists(self._path_of_file):
        #     os.remove(self._path_of_file)

        err_cnt = 0
        while True:
            try:
                cur_page = self._session.get(cur_url, headers = self._headers)
            except:
                time.sleep(1)
                err_cnt = err_cnt + 1
                if err_cnt == 3:
                    break

            if not cur_page:
                continue

            cur_page.encoding = "utf-8"
            bsobj = BeautifulSoup(cur_page.text, "html.parser")

            blacklist = bsobj.findAll("td")
            if not blacklist:
                break

            for hei in blacklist:
                
                
                ph_num = hei.get_text().strip()

                if re.match(r'^[0-9]{8,}$', ph_num):

                    with open(self._path_of_file, 'a') as f:
                        f.write(ph_num + '\n')
                    
                    print(ph_num)
                    cnt = cnt + 1

            

            print('\n----------------------------num: ' + str(cnt) + '\n')
            break



if __name__ == '__main__':

    szjf_spider = szjf()
    szjf_spider.start()
