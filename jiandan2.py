import urllib
from urllib.request import urlopen
from bs4 import BeautifulSoup
from selenium import webdriver
from multiprocessing import Process, Pool, Queue
import re
import os
import imghdr
import time



headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) \
    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
}
index = 1

start_url = "http://jandan.net/ooxx"

pic_dir = "./jiandan_pic"

def init_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)
    else:
        for f in os.listdir(path):
            path = os.path.join(path, f)
            os.remove(path)

def get_pic_in_current_page(curr_url, process_pool):

    driver.get(curr_url)
    time.sleep(3)
    html = driver.page_source
    bsObj = BeautifulSoup(html, "html.parser")

    next_url = bsObj.find("div", {"class":"cp-pagenavi"}).find("a", {"class":"previous-comment-page"}).attrs["href"]
    if next_url:
        matchobj = re.match(r'page-([0-9]+)', next_url)
        page_num = int(matchobj.group(1))
        print ("page %d will be crawed!" % page_num)



    while True:

        #不用selenium难以爬去动态页面
        #webRequest = urllib.request.Request(next_url, headers=headers)
        #html = urlopen(webRequest)



        list_item = bsObj.find("ol", {"class":"commentlist"}).findAll("li")
        for item in list_item:
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
            
                content = urlopen("http:" + src).read()

                file_name = "jiandan_" + str(index)
                file_path = os.path.join("./jiandan_pic", file_name)
                
                if not content:
                    continue
                imgtype = imghdr.what('', h = content)
                if not imgtype:
                    continue

                with open(file_path + "." + imgtype, "wb") as picfile:
                    picfile.write(content)

                index = index + 1









driver = webdriver.PhantomJS(executable_path = '../phantomjs/bin/phantomjs.exe')
process_pool = Pool(4)
get_pic_in_current_page(start_url, process_pool)

driver.close()