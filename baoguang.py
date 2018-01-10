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
        db = client.baoguang #选择数据
        self.blacks = db.blacks #选择集合book

    #添加、删除、查找的内部接口

    def is_empty(self, coll):
        return coll.find().count() == 0


    def del_all_from_coll(self, coll):
        coll.remove()

    #外部接口

    def init_all_colls(self):
        self.del_all_from_coll(self.blacks)

    def del_black_coll(self):
        self.del_all_from_coll(self.blacks)

    def save_one_black(self, black):
        black_d = {"ph_num":black}
        if self.blacks.find(black_d).count() == 0:
            self.blacks.insert(black_d)

        if self.blacks.find().count() % 10 == 0:
            pass
            #self.output_to_xls()
            #self.output_to_txt()
            #self.del_black_coll()            

    def output_to_txt(self):
        allDatas = self.blacks.find()
        
        for data in allDatas:
            with open("../baoguang.txt", 'a') as f:
                f.write(data["ph_num"] + '\n')                                                                          

        

    def output_to_xls(self):
 
        if not os.path.exists("../black2345.xls"):
            w = xlwt.Workbook() 
            ws = w.add_sheet('2345') 
            ws.write(0,0,u'序号')
            ws.write(0,1,u'号码')
            ws.write(0,2,u'原因')
            ws.write(0,3,u'举报人数')
            row = 1
        else:
            oldwb = xlrd.open_workbook("../black2345.xls")
            row = oldwb.sheets()[0].nrows
            w = copy(oldwb)
            ws = w.get_sheet(0)
            

        print("current row: " + str(row))
        allDatas = self.blacks.find()
        
        for data in allDatas:
            print("------write to xls.")
            ws.write( row, 0, row )
            if not 'ph_num' in data:
                continue
            ws.write( row, 1, data['ph_num'] )
            if 'reason' in data:
                ws.write( row, 2, data['reason'] )
            
            if 'num' in data:
                ws.write( row, 3, data['num'] )                                                                           
                
            row += 1

        w.save('../black2345.xls') #保存        




class baoguang(object):
    def __init__(self):
        self._catalog_url = "http://www.pianziweb.com/"
        self._session = requests.Session()
        self._headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) \
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
        }
        
        self._path_of_file = "../baoguang.txt"

        self._mongo = Mongo()


    def start(self):

        self._mongo.init_all_colls()

        cur_url = self._catalog_url + "guhua_25_1.html"
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
            
            blacklist = bsobj.findAll("li", {"class":re.compile("^col-xs-12")})

            if not blacklist:
                break

            for hei in blacklist:
                
                span = hei.find("span", {"class":"fl"})
                if span:
                    ph_num = span.next_sibling.get_text()

                

                print(ph_num)

                self._mongo.save_one_black(ph_num)
                
                cnt = cnt + 1

            page_cnt = page_cnt + 1

            if page_cnt == 206:
                break 

            cur_url = self._catalog_url + "guhua_25_" + str(page_cnt) + ".html"

            print('\n----------------------------num: ' + str(cnt) + '\n')
            print('\n----------------------------pages: ' + str(page_cnt) + '\n')

        self._mongo.output_to_txt()
        self._mongo.del_black_coll()


if __name__ == '__main__':

    baoguang_spider = baoguang()
    baoguang_spider.start()
