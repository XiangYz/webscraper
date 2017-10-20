import urllib
from urllib.request import urlopen
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from multiprocessing import Process, Pool, Queue
import re
import os
import imghdr
import time
import logging


pages_to_be_crawled = 10


def handle_first_page(url, process_pool, dir):

    driver = webdriver.PhantomJS(executable_path = '../phantomjs/bin/phantomjs.exe')
    #driver = webdriver.Chrome(executable_path="./chromedriver")
    driver.get(url)

    #time.sleep(3)
    #等待3s有时候会浪费时间
    element = WebDriverWait(driver, 3).until(
        EC.presence_of_element_located((By.XPATH, "//a[@title='Older Comments']"))
    )

    if not element:
        driver.close()
        #logging.info("first page get failed")    
        return
    #logging.info("first page get finished")


    html = driver.page_source
    bsObj = BeautifulSoup(html, "html.parser")
    
    # 查看当前的页码
    current_page_num = bsObj.find("div", {"class":"cp-pagenavi"}).find("span", {"class":"current-comment-page"}).get_text()
    current_page_num = re.match("\[([0-9]+)\]", current_page_num).group(1)
    current_page_num = int(current_page_num)
    

    # 开启进程爬取其它页面
    i = 1
    while True:
        if i >= pages_to_be_crawled:
            break
        next_page_num = current_page_num - i
        i = i + 1
        next_url = url + "/page-" + str(next_page_num) + "#comments"
        process_pool.apply_async(handle_other_pages, args=(next_url, next_page_num, dir))

    # 爬取本页面
    #logging.info("first page will be crawed!")
    get_pic_in_current_page(bsObj, current_page_num, dir)
    #logging.info("first page crawl finished")

    process_pool.close()
    process_pool.join()

    driver.close()


def handle_other_pages(curr_url, page_num, dir):

    #driver = webdriver.PhantomJS(executable_path = '../phantomjs/bin/phantomjs.exe')
    driver = webdriver.Chrome(executable_path="./chromedriver")

    driver.get(curr_url)

    #time.sleep(3)
    #等待3s有时候会浪费时间
    element = WebDriverWait(driver, 3).until(
        EC.presence_of_element_located((By.XPATH, "//a[@title='Older Comments']"))
    )

    
    if not element:
        driver.close()
        #logging.info("page" + page_num + " get failed")    
        return
    #logging.info("page" + page_num + " get finished")

    html = driver.page_source
    bsObj = BeautifulSoup(html, "html.parser")

    get_pic_in_current_page(bsObj, page_num, dir)
    #logging.info("page" + page_num + " crawl finished")

    driver.close()

def get_pic_in_current_page(bsObj, page_num, dir):

    index = 1

    list_item = bsObj.find("ol", {"class":"commentlist"}).findAll("li")
    for item in list_item:
        '''
        publish_time = item.find("div", {"class":"row"}).find("div", {"class":"author"}).find("small").find("a").get_text()
        pub_time_list = publish_time.split()
        if pub_time_list[1].lower() == "weeks":
            stop = True
            break
        elif pub_time_list[1].lower() == "days":
            days = pub_time_list[0][1:]
            if int(days) >= 6:
                stop = True
                break
        '''

        img_items = item.find("div", {"class":"row"})
        img_items = img_items.find("div", {"class":"text"})
        img_items = img_items.findAll("img")
        for img_item in img_items:
            src = img_item.attrs["src"]
            if not src:
                continue
        
            pos = src.rfind(".gif")
            if pos > 0:
                org_src = img_item.attrs["org_src"]
                if not org_src:
                    continue
                src = org_src

            # 采用urlopen获得图片数据
            # content = urlopen("http:" + src).read()
            # 采用requests获得图片数据
            content = requests.get("http:" + src, timeout=10).content
            if not content:
                #logging.info("url: http:" + src + " get failed")
                continue

            file_name = "jiandan_page" + str(page_num) + "_" + str(index)
            file_path = os.path.join(dir, file_name)
            
            imgtype = imghdr.what('', h = content)
            if not imgtype:
                continue

            with open(file_path + "." + imgtype, "wb") as picfile:
                picfile.write(content)
                

            index = index + 1


def init_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)
    else:
        for f in os.listdir(path):
            filepath = os.path.join(path, f)
            os.remove(filepath)


if __name__ == '__main__':
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) \
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
    }

    start_url = "http://jandan.net/ooxx"
    pic_dir = "./jiandan_pic"

    init_dir(pic_dir)

    #logging.basicConfig(level = logging.info)

    process_pool = Pool(4)
    handle_first_page(start_url, process_pool, pic_dir)
    #logging.info("DONE")
