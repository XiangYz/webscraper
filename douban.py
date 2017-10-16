import urllib
from urllib.request import urlopen
from bs4 import BeautifulSoup
from selenium import webdriver
import re
import os
import imghdr
import time
import requests
import pymongo
import sys
import xlwt
import xlrd
import random

class Mongo(object):
    def __init__(self):
        client = pymongo.MongoClient('localhost', 27017) #连接服务器
        db = client.douban #选择数据库
        self.newUrlsColl = db.newUrls #选择集合newUrls
        self.oldUrlsColl = db.oldUrls #选择集合oldUrls
        self.bookColl = db.book #选择集合book

    #添加、删除、查找的内部接口
    def add_url_direct(self, coll, url):
        if url is None or url is '':
            return
        coll.insert({'url':url})

    def is_url_in_coll(self, coll, url):
        if url is None or url is '':
            return
        if coll.find({'url':url}).count() == 0:
            return False
        return True

    def add_url_checked(self, coll, url):
        if url is None or url is '':
            return
        if self.is_url_in_coll(coll, url):
            return
        self.add_url_direct(coll, url)

    def is_empty(self, coll):
        return coll.find().count() == 0

    def del_url_from_coll(self, coll, url):
        coll.remove(url)

    def del_all_urls_from_coll(self, coll):
        coll.remove()

    #外部接口
    def add_new_url(self, url):
        if self.is_url_in_coll(self.oldUrlsColl, url):
            return
        self.add_url_checked(self.newUrlsColl, url)

    def get_new_url(self):
        if self.is_empty(self.newUrlsColl):
            return ''
        url = self.newUrlsColl.find_one()
        self.del_url_from_coll(self.newUrlsColl, url)
        self.add_url_checked(self.oldUrlsColl, url)

        return url['url']

    def init_all_colls(self):
        self.del_all_urls_from_coll(self.newUrlsColl)
        self.del_all_urls_from_coll(self.oldUrlsColl)
        self.del_all_urls_from_coll(self.bookColl)

    def save_one_book(self, book):
        self.bookColl.insert(book)

    def output_to_xls(self):
        '''
        excelFile = unicode('GoodBooks.xls', 'utf8')
        wbk = xlwt.Workbook()
        sheet = wbk.add_sheet('douban', cell_overwrite_ok = True)
        headList = ['No.', 'name', 'score', 'price', 'press', 'author', 'url']
        row_index = 0
        for i in range(0,len(headList)):
            sheet.write(0, i, headList[i], set_style('Times New Roman', 220, True))
        '''
        allDatas = self.bookColl.find()

        w = xlwt.Workbook() #创建一个工作簿
        ws = w.add_sheet('douban') #创建一个工作表
        ws.write(0,0,u'序号')
        ws.write(0,1,u'书名')
        ws.write(0,2,u'评分')
        ws.write(0,3,u'作者')
        ws.write(0,4,u'价格')
        ws.write(0,5,u'出版社')
        ws.write(0,6,u'出版年')
        ws.write(0,7,u'页数')
        ws.write(0,8,u'ISBN')
        ws.write(0,9,u'url')
        row = 1
        for data in allDatas:
            ws.write( row, 0, row )
            ws.write( row, 1, data['name'] )
            ws.write( row, 2, float(data['rate']) )
            ws.write( row, 3, data['author'] )
            ws.write( row, 4, data['price'] )
            ws.write( row, 5, data['press'] )
            ws.write( row, 6, data['ym'] )
            ws.write( row, 7, data['pages'] )
            ws.write( row, 8, data['ISBN'] )
            ws.write( row, 9, data['url'] )
            row += 1
        w.save('GoodBooks.xls') #保存


class Douban(object):
    def __init__(self, start_url):
        self.start_url = start_url
        self.session = requests.Session()
        self.headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        }

        self.mongo = Mongo()
        
    
    def crawl_one_page(self, bsobj):
        book = {}

        name = bsobj.findAll("span", {"property":"v:itemreviewed"})
        if name:
            book['name'] = name[0].get_text()

        book['rate'] = bsobj.find("strong", {"class":re.compile("rating_num"), "property":"v:average"}).get_text()
    
        infoobj = bsobj.find("div", {"id":"info"})

        author = infoobj.findAll("span", text=re.compile("作者"))  #这个地方不能用find，真奇怪
        if author:
            book['author'] = author[0].next_sibling.next_sibling.get_text().strip().replace("\n", "")
            book['author'] = re.sub(r'\s+', ' ', book['author'])
        
        press = infoobj.findAll("span", text=re.compile("出版社"))
        if press:
            book['press'] = press[0].next_sibling.string.strip().replace("\n", "")
   
        origin_name = infoobj.findAll("span", text=re.compile("原作名"))
        if origin_name:
            book['origin_name'] = origin_name[0].next_sibling.string.strip().replace("\n", "")

        ym = infoobj.findAll("span", text=re.compile("出版年"))
        if ym:
            book['ym'] = ym[0].next_sibling.string.strip().replace("\n", "")

        pages = infoobj.findAll("span", text=re.compile("页数"))
        if pages:
            book['pages'] = pages[0].next_sibling.string.strip().replace("\n", "")

        price = infoobj.findAll("span", text=re.compile("定价"))
        if price:
            book['price'] = price[0].next_sibling.string.strip().replace("\n", "")

        ISBN = infoobj.findAll("span", text=re.compile("ISBN"))
        if ISBN:
            book['ISBN'] = ISBN[0].next_sibling.string.strip().replace("\n", "")

        translators = infoobj.findAll("span", text=re.compile('译者'))
        if translators:
            translators = translators[0].parent
            book['translator'] = []
            translators = translators.findAll("a")
            for ele in translators:
                ele = re.sub(r'\s+.*$', '', ele.get_text())
                book['translator'].append(ele)


        print (book)

        return book
    
    def start_crawl(self):

        self.mongo.init_all_colls()
        cnt = 0
        #将起始url放入待爬取集合内
        self.mongo.add_new_url(start_url)
        while True:
            #从待爬取集合内取出一个url
            next_url = self.mongo.get_new_url()
            print(next_url)
            if next_url == '':
                break

            #爬取当前页面
            page = self.session.get(next_url, headers = self.headers)
            bsobj = BeautifulSoup(page.content, "html.parser", from_encoding='utf-8')
            book = self.crawl_one_page(bsobj)
            book['url'] = next_url
            #存储书籍信息
            self.mongo.save_one_book(book)
            time.sleep(random.uniform(0.1, 0.3))
            #寻找关联url放到待爬取url集合中
            rel_imgs = bsobj.findAll("img", {"class":"m_sub_img"})
            for img in rel_imgs:
                rel_url = img.parent.attrs['href']
                self.mongo.add_new_url(rel_url)
            
            cnt = cnt + 1
            if cnt == 3:
                break
        
        self.mongo.output_to_xls()

if __name__ == '__main__':
    start_url = "https://book.douban.com/subject/1477390/"
    douban_spider = Douban(start_url)
    douban_spider.start_crawl()