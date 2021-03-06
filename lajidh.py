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

        


class Mongo(object):
    def __init__(self):
        client = pymongo.MongoClient('localhost', 27017) #连接服务
        db = client.lajidh #选择数据
        self.blacks = db.lajidh_c #选择集合book
        self.all_blacks = db.lajidh_ca

    #添加、删除、查找的内部接口

    def is_empty(self, coll):
        return coll.find().count() == 0


    def del_all_from_coll(self, coll):
        coll.remove()

    #外部接口

    def init_all_colls(self):
        self.del_all_from_coll(self.blacks)
        self.del_all_from_coll(self.all_blacks)

    def del_black_coll(self):
        self.del_all_from_coll(self.blacks)

    def save_one_black(self, black):
        black_d = {"ph_num":black}
        if self.all_blacks.find(black_d).count() == 0:
            self.blacks.insert(black_d)
            self.all_blacks.insert(black_d)

        if self.blacks.find().count() % 10 == 0:
            #pass
            #self.output_to_xls()
            self.output_to_txt()
            self.del_black_coll()            

    def output_to_txt(self):
        allDatas = self.blacks.find()
        
        for data in allDatas:
            with open("../lajidianhua.txt", 'a') as f:
                f.write(data["ph_num"] + '\n')     




class lajidh(object):
    def __init__(self):
        self._catalog_url = "http://www.lajidianhua.com"
        self._session = requests.Session()
        self._headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) \
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
        }
        
        self._path_of_file = "../lajidianhua.txt"

        self._mongo = Mongo()


    def start(self):

        self._mongo.init_all_colls()

        cur_url = self._catalog_url + "/list-8-183147-1.html"
        cnt = 0
        page_cnt = 0

        if os.path.exists(self._path_of_file):
            os.remove(self._path_of_file)


        while True:
            try:
                cur_page = self._session.get(cur_url, headers = self._headers)
            except:
                break
            if not cur_page:
                break

            cur_page.encoding = "utf-8"
            bsobj = BeautifulSoup(cur_page.text, "html.parser")
            
            blacklist = bsobj.find("ul", {"class":"e2"})
            if blacklist:
                blacklist = blacklist.findAll("table")
            if not blacklist:
                break

            for hei in blacklist:
                
                ph_num = hei.find("a").get_text()

                if re.match(r'^[0-9]+$', ph_num):
                    self._mongo.save_one_black(ph_num)
                    print(ph_num)
                    cnt = cnt + 1

            page_cnt = page_cnt + 1

            #if page_cnt == 7326:
                #break 

            next_page = bsobj.findAll("a", text=re.compile("下一页"))
            if not next_page:
                break
            cur_url = self._catalog_url + next_page[0].attrs['href']

            print('\n----------------------------num: ' + str(cnt) + '\n')
            print('\n----------------------------pages: ' + str(page_cnt) + '\n')

        self._mongo.output_to_txt()
        self._mongo.init_all_colls()


if __name__ == '__main__':

    lajidh_spider = lajidh()
    lajidh_spider.start()
