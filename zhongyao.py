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
        db = client.zhongyao #选择数据
        self.newUrlsColl = db.newUrls #选择集合newUrls
        self.oldUrlsColl = db.oldUrls #选择集合oldUrls
        self.yaoColl = db.yao #选择集合book

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

    def del_all_from_coll(self, coll):
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
        self.del_all_from_coll(self.newUrlsColl)
        self.del_all_from_coll(self.oldUrlsColl)
        self.del_all_from_coll(self.yaoColl)

    def del_yao_coll(self):
        self.del_all_from_coll(self.yaoColl)

    def save_one_yao(self, yao):
        if self.yaoColl.find(yao).count() == 0:
            self.yaoColl.insert(yao)

        if self.yaoColl.find().count() % 10 == 0:
            self.output_to_xls()
            self.del_yao_coll()            

    def output_to_xls(self):
 
        if not os.path.exists("zhongyao/中药.xls"):
            w = xlwt.Workbook() 
            ws = w.add_sheet('中药') 
            ws.write(0,0,u'序号')
            ws.write(0,1,u'药名')
            ws.write(0,2,u'别名')
            ws.write(0,3,u'英文名')
            ws.write(0,4,u'来源')
            ws.write(0,5,u'植物形态')
            ws.write(0,6,u'产地分布')
            ws.write(0,7,u'采收加工')
            ws.write(0,8,u'药材性状')
            ws.write(0,9,u'性味归经')
            ws.write(0,10,u'功效与作用')
            ws.write(0,11,u'临床应用')
            ws.write(0,12,u'药理研究')
            ws.write(0,13,u'化学成分')
            ws.write(0,14,u'使用禁忌')
            ws.write(0,15,u'相关药方')
            row = 1
        else:
            oldwb = xlrd.open_workbook("zhongyao/中药.xls")
            row = oldwb.sheets()[0].nrows
            w = copy(oldwb)
            ws = w.get_sheet(0)
            

        print("current row: " + str(row))
        allDatas = self.yaoColl.find()
        
        for data in allDatas:
            print("------write to xls.")
            ws.write( row, 0, row )
            if not 'name' in data:
                continue
            ws.write( row, 1, data['name'] )
            if 'alias' in data:
                ws.write( row, 2, data['alias'] )
            
            if 'eng_name' in data:
                ws.write( row, 3, data['eng_name'] )
            
            if 'source' in data:
                ws.write( row, 4, data['source'] )
            
            if 'shape' in data:
                ws.write( row, 5, data['shape'] )
            
            if 'place' in data:
                ws.write( row, 6, data['place'] )
            
            if 'handling' in data:
                ws.write( row, 7, data['handling'] )
            
            if 'property' in data:
                ws.write( row, 8, data['property'] )
            
            if 'tropism' in data:
                ws.write( row, 9, data['tropism'] )

            if 'efficiency' in data:
                ws.write( row, 10, data['efficiency'] )

            if 'clinic' in data:
                ws.write( row, 11, data['clinic'] )

            if 'pharmacodynamics' in data:
                ws.write( row, 12, data['pharmacodynamics'] )

            if 'chemical composition' in data:
                ws.write( row, 13, data['chemical composition'] ) 

            if 'contraindication' in data:
                ws.write( row, 14, data['contraindication'] )

            if 'prescript' in data:
                ws.write( row, 15, data['prescript'] )                                                                               
                
            row += 1

        w.save('zhongyao/中药.xls') #保存
        

class zhongyao(object):
    def __init__(self):
        self._catalog_url = "http://www.zhongyoo.com/name/"
        self._session = requests.Session()
        self._headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) \
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
        }
        
        self._mongo = Mongo()

    def start(self):

        self._mongo.init_all_colls()

        cur_url = self._catalog_url
        cnt = 0
        while True:
            try:
                cur_page = self._session.get(cur_url, headers = self._headers)
            except:
                break
            if not cur_page:
                break

            cur_page.encoding = "GB2312"
            bsobj = BeautifulSoup(cur_page.text, "html.parser")
            zhongyaos = bsobj.findAll("div", {"class":"sp"})
            if not zhongyaos:
                break
            for zhongyao in zhongyaos:
                link = zhongyao.find("a", {"class":"title"}).attrs['href']
                link = "http://www.zhongyoo.com" + link
                print(link)
                cnt = cnt + 1
                self._mongo.add_new_url(link)

            pagelist = bsobj.find("ul", {"class":"pagelist"})
            next_page = pagelist.findAll("a", text=re.compile("下一页"))
            if not next_page:
                break
            cur_url = self._catalog_url + next_page[0].attrs['href']

        print('url num: ' + str(cnt))

        # process_pool = Pool()
        # for i in range(4):
        #     process_pool.apply_async(get_zhongyao)

        # process_pool.close()
        # process_pool.join()

        self.get_zhongyao()

    def get_zhongyao(self):

        session = requests.Session()
        headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) \
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
        }

        #mongo = Mongo()
        mongo = self._mongo
        
        while True:
            next_url = mongo.get_new_url()
            print(next_url)
            if next_url == '' or next_url is None:
                break

            yao = {}

            page = session.get(next_url, headers=headers)
            page.encoding = 'GB2312'
            bsobj = BeautifulSoup(page.text, "html.parser")

            yao['name'] = bsobj.find("div", {"class":"title"}).find("h1").get_text()
                    
            alias_obj = bsobj.findAll("strong", text=re.compile("别名"))
            if alias_obj:
                yao['alias'] = alias_obj[0].parent.get_text().replace("\r\n\t\u3000\u3000【别名】", "")
            
            eng_name_obj = bsobj.findAll("strong", text=re.compile("英文名"))
            if eng_name_obj:
                yao['eng_name'] = eng_name_obj[0].parent.get_text().replace("\r\n\t\u3000\u3000【英文名】", "")

            source_obj = bsobj.findAll("strong", text=re.compile("来源"))
            if source_obj:
                yao['source'] = source_obj[0].parent.get_text().replace("\r\n\t\u3000\u3000【来源】", "")    

            shape_obj = bsobj.findAll("strong", text=re.compile("植物形态"))
            if shape_obj:
                yao['shape'] = shape_obj[0].parent.get_text().replace("\r\n\t\u3000\u3000【植物形态】", "")          

            place_obj = bsobj.findAll("strong", text=re.compile("产地分布"))
            if place_obj:
                yao['place'] = place_obj[0].parent.get_text().replace("\r\n\t\u3000\u3000【产地分布】", "")  
            else:
                place_obj = bsobj.findAll("strong", text=re.compile("生境分布"))
                if place_obj:
                    yao['place'] = place_obj[0].parent.get_text().replace("\r\n\t\u3000\u3000【生境分布】", "")  

            handling_obj = bsobj.findAll("strong", text=re.compile("采收加工"))
            if handling_obj:
                yao['handling'] = handling_obj[0].parent.get_text().replace("\r\n\t\u3000\u3000【采收加工】", "")      

            property_obj = bsobj.findAll("strong", text=re.compile("药材性状"))
            if property_obj:
                yao['property'] = property_obj[0].parent.get_text().replace("\r\n\t\u3000\u3000【药材性状】", "")                                                                 
            
            tropism_obj = bsobj.findAll("strong", text=re.compile("性味归经"))
            if tropism_obj:
                yao['tropism'] = tropism_obj[0].parent.get_text().replace("\r\n\t\u3000\u3000【性味归经】", "")     

            efficiency_obj = bsobj.findAll("strong", text=re.compile("功效与作用"))
            if efficiency_obj:
                yao['efficiency'] = efficiency_obj[0].parent.get_text().replace("\r\n\t\u3000\u3000【功效与作用】", "")           

            clinic_obj = bsobj.findAll("strong", text=re.compile("临床应用"))
            if clinic_obj:
                yao['clinic'] = clinic_obj[0].parent.get_text().replace("\r\n\t\u3000\u3000【临床应用】", "")                                        
            
            pharmacodynamics_obj = bsobj.findAll("strong", text=re.compile("药理研究"))
            if pharmacodynamics_obj:
                yao['pharmacodynamics'] = pharmacodynamics_obj[0].parent.get_text().replace("\r\n\t\u3000\u3000【药理研究】", "") 

            composition_obj = bsobj.findAll("strong", text=re.compile("化学成分"))
            if composition_obj:
                yao['chemical composition'] = composition_obj[0].parent.get_text().replace("\r\n\t\u3000\u3000【化学成分】", "") 

            contraindication_obj = bsobj.findAll("strong", text=re.compile("使用禁忌"))
            if contraindication_obj:
                yao['contraindication'] = contraindication_obj[0].parent.get_text().replace("\r\n\t\u3000\u3000【使用禁忌】", "") 

            prescript_obj = bsobj.findAll("strong", text=re.compile("相关药方"))
            if prescript_obj:
                yao['prescript'] = prescript_obj[0].parent.get_text().replace("\r\n\t\u3000\u3000【相关药方】", "")     

            print(yao['name'])

            mongo.save_one_yao(yao)                                                        

            img_link = bsobj.find("img")
            if img_link:
                img_link = img_link.attrs['src']
                img_link = "http://www.zhongyoo.com" + img_link

                try:
                    img = session.get(img_link).content
                except:
                    continue

                imgtype = imghdr.what('', h = img)
                if imgtype:
                    file_name = yao['name']
                    file_path = "zhongyao/" + file_name 
                    with open(file_path + "." + imgtype, "wb") as picfile:
                        picfile.write(img)


if __name__ == '__main__':

    # session = requests.Session()
    # headers = {
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) \
    #     AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
    # }
    # page = session.get("http://www.zhongyoo.com/name/danggui_142.html", headers=headers)
    # page.encoding = 'GB2312'
    # bsobj = BeautifulSoup(page.text, "html.parser")

    # yao = {}
    # yao['name'] = bsobj.find("div", {"class":"title"}).find("h1").get_text()
            
    # alias_obj = bsobj.findAll("strong", text=re.compile("别名"))
    # if alias_obj:
    #     yao['alias'] = alias_obj[0].parent.get_text().replace("\r\n\t\u3000\u3000【别名】", "")
    
    # eng_name_obj = bsobj.findAll("strong", text=re.compile("英文名"))
    # if eng_name_obj:
    #     yao['eng_name'] = eng_name_obj[0].parent.get_text().replace("\r\n\t\u3000\u3000【英文名】", "")

    # source_obj = bsobj.findAll("strong", text=re.compile("来源"))
    # if source_obj:
    #     yao['source'] = source_obj[0].parent.get_text().replace("\r\n\t\u3000\u3000【来源】", "")    

    # shape_obj = bsobj.findAll("strong", text=re.compile("植物形态"))
    # if shape_obj:
    #     yao['shape'] = shape_obj[0].parent.get_text().replace("\r\n\t\u3000\u3000【植物形态】", "")          

    # place_obj = bsobj.findAll("strong", text=re.compile("产地分布"))
    # if place_obj:
    #     yao['place'] = place_obj[0].parent.get_text().replace("\r\n\t\u3000\u3000【产地分布】", "")  
    # else:
    #     place_obj = bsobj.findAll("strong", text=re.compile("生境分布"))
    #     if place_obj:
    #         yao['place'] = place_obj[0].parent.get_text().replace("\r\n\t\u3000\u3000【生境分布】", "")  

    # handling_obj = bsobj.findAll("strong", text=re.compile("采收加工"))
    # if handling_obj:
    #     yao['handling'] = handling_obj[0].parent.get_text().replace("\r\n\t\u3000\u3000【采收加工】", "")      

    # property_obj = bsobj.findAll("strong", text=re.compile("药材性状"))
    # if property_obj:
    #     yao['property'] = property_obj[0].parent.get_text().replace("\r\n\t\u3000\u3000【药材性状】", "")                                                                 
    
    # tropism_obj = bsobj.findAll("strong", text=re.compile("性味归经"))
    # if tropism_obj:
    #     yao['tropism'] = tropism_obj[0].parent.get_text().replace("\r\n\t\u3000\u3000【性味归经】", "")     

    # efficiency_obj = bsobj.findAll("strong", text=re.compile("功效与作用"))
    # if efficiency_obj:
    #     yao['efficiency'] = efficiency_obj[0].parent.get_text().replace("\r\n\t\u3000\u3000【功效与作用】", "")           

    # clinic_obj = bsobj.findAll("strong", text=re.compile("临床应用"))
    # if clinic_obj:
    #     yao['clinic'] = clinic_obj[0].parent.get_text().replace("\r\n\t\u3000\u3000【临床应用】", "")                                        
    
    # pharmacodynamics_obj = bsobj.findAll("strong", text=re.compile("药理研究"))
    # if pharmacodynamics_obj:
    #     yao['pharmacodynamics'] = pharmacodynamics_obj[0].parent.get_text().replace("\r\n\t\u3000\u3000【药理研究】", "") 

    # composition_obj = bsobj.findAll("strong", text=re.compile("化学成分"))
    # if composition_obj:
    #     yao['chemical composition'] = composition_obj[0].parent.get_text().replace("\r\n\t\u3000\u3000【化学成分】", "") 

    # contraindication_obj = bsobj.findAll("strong", text=re.compile("使用禁忌"))
    # if contraindication_obj:
    #     yao['contraindication'] = contraindication_obj[0].parent.get_text().replace("\r\n\t\u3000\u3000【使用禁忌】", "") 

    # prescript_obj = bsobj.findAll("strong", text=re.compile("相关药方"))
    # if prescript_obj:
    #     yao['prescript'] = prescript_obj[0].parent.get_text().replace("\r\n\t\u3000\u3000【相关药方】", "")     

    # print(yao)
    # #self._mongo.save_one_yao(yao)                                                        

    # img_link = bsobj.find("img").attrs['src']
    # img_link = "http://www.zhongyoo.com" + img_link
    # img = session.get(img_link).content

    # imgtype = imghdr.what('', h = img)
    # if imgtype:
    #     file_name = yao['name']
    #     file_path = "zhongyao/" + file_name 
    #     with open(file_path + "." + imgtype, "wb") as picfile:
    #         picfile.write(img)



    if os.path.exists("zhongyao"):
        for f in os.listdir("zhongyao"):
            filepath = os.path.join("zhongyao", f)
            os.remove(filepath)
    else:
        os.mkdir("zhongyao")

    zhongyao_spider = zhongyao()
    zhongyao_spider.start()
