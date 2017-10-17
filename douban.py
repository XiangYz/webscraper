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
            return False
        self.add_url_direct(coll, url)
        return True

    def is_empty(self, coll):
        return coll.find().count() == 0

    def del_url_from_coll(self, coll, url):
        coll.remove({'url':url})

    def del_all_urls_from_coll(self, coll):
        coll.remove()

    #外部接口
    def add_new_url(self, url):
        if self.is_url_in_coll(self.oldUrlsColl, url):
            return False
        return self.add_url_checked(self.newUrlsColl, url)
    

    def get_new_url(self):
        if self.is_empty(self.newUrlsColl):
            return ''
        url = self.newUrlsColl.find_one()
        self.del_url_from_coll(self.newUrlsColl, url['url'])
        self.add_url_checked(self.oldUrlsColl, url['url'])

        return url['url']

    def init_all_colls(self):
        self.del_all_urls_from_coll(self.newUrlsColl)
        self.del_all_urls_from_coll(self.oldUrlsColl)
        self.del_all_urls_from_coll(self.bookColl)

    def save_one_book(self, book):
        if self.bookColl.find(book).count() == 0:
            self.bookColl.insert(book)

    def output_to_xls(self):
 
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
            print("------write to xls.")
            ws.write( row, 0, row )
            if not 'name' in data:
                continue
            ws.write( row, 1, data['name'] )
            if 'rate' in data:
                ws.write( row, 2, data['rate'] )
            
            if 'author' in data:
                ws.write( row, 3, data['author'] )
            
            if 'price' in data:
                ws.write( row, 4, data['price'] )
            
            if 'press' in data:
                ws.write( row, 5, data['press'] )
            
            if 'ym' in data:
                ws.write( row, 6, data['ym'] )
            
            if 'pages' in data:
                ws.write( row, 7, data['pages'] )
            
            if 'ISBN' in data:
                ws.write( row, 8, data['ISBN'] )
            
            if 'url' in data:
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
        
    def logon(self, username, passwd):
        # source=None&redir=https://www.douban.com&form_email=18666219953&form_password=5555WJXBH&login=登录
        params = {
            'source':'None',
            'redir':'https://www.douban.com',
            'form_email':username,
            'form_password':passwd,
            'login':u'登录'
        }
        r = self.session.post("https://accounts.douban.com/login", data = params)
        
        return r.status_code
    
    def crawl_one_page(self, bsobj):
        book = {}

        name = bsobj.findAll("span", {"property":"v:itemreviewed"})
        if name:
            book['name'] = name[0].get_text()

        rate = bsobj.findAll("strong", {"class":re.compile("rating_num"), "property":"v:average"})
        if rate:
            book['rate'] = rate[0].get_text()
    
        infoobj = bsobj.find("div", {"id":"info"})
        if not infoobj:
            print("-----no info")
            return book

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
        rcode = self.logon('18666219953', '5555WJXBH')
        print('-----login ret: ' + str(rcode))
        self.mongo.init_all_colls()
        cnt = 0
        #将起始url放入待爬取集合内
        self.mongo.add_new_url(start_url)
        while True:
            #从待爬取集合内取出一个url
            next_url = self.mongo.get_new_url()
            print(next_url)
            if next_url == '':
                print('all books are crawled.')
                break

            #爬取当前页面
            while True:
                try:
                    page = self.session.get(next_url, headers = self.headers)
                    break
                except:
                    print('-----get page except.')
                    time.sleep(random.uniform(3, 5))
                    continue

            bsobj = BeautifulSoup(page.content, "html.parser", from_encoding='utf-8')
            book = self.crawl_one_page(bsobj)
            if book:
                book['url'] = next_url
                #存储书籍信息
                self.mongo.save_one_book(book)
                cnt = cnt + 1
            time.sleep(random.uniform(0.3, 0.5))
            #寻找关联url放到待爬取url集合中
            rel_imgs = bsobj.findAll("img", {"class":"m_sub_img"})
            if not rel_imgs:
                continue
            for img in rel_imgs:
                rel_url = img.parent.attrs['href']
                self.mongo.add_new_url(rel_url)
            
            if cnt == 200:
                break
        
        self.mongo.output_to_xls()

if __name__ == '__main__':
    start_url = "https://book.douban.com/subject/1477390/"
    douban_spider = Douban(start_url)
    douban_spider.start_crawl()