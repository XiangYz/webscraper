import urllib
from urllib.request import urlopen
from bs4 import BeautifulSoup
from selenium import webdriver
import re
import os
import imghdr
import time



headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) \
    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
}
index = 1
stop = False
next_url = "http://jandan.net/ooxx"



if not os.path.exists(".\\jiandan_pic"):
    os.mkdir("jiandan_pic")
else:
    for f in os.listdir(".\\jiandan_pic"):
        path = os.path.join(".\\jiandan_pic", f)
        os.remove(path)


driver = webdriver.PhantomJS(executable_path = '../phantomjs/bin/phantomjs.exe')



while True:

    #webRequest = urllib.request.Request(next_url, headers=headers)
    #html = urlopen(webRequest)

    driver.get(next_url)
    html = driver.page_source

    time.sleep(3)

    bsObj = BeautifulSoup(html, "html.parser")

    list_item = bsObj.find("ol", {"class":"commentlist"}).findAll("li")
    for item in list_item:
        publish_time = item.find("div", {"class":"row"}).find("div", {"class":"author"}).find("small").find("a").get_text()
        pub_time_list = publish_time.split()
        if pub_time_list[1].lower() == "weeks":
            stop = True
            break
        elif pub_time_list[1].lower() == "days":
            days = pub_time_list[0][1:]
            if int(days) >= 1:
                stop = True
                break
        
        img_item = item.find("div", {"class":"row"})
        img_item = img_item.find("div", {"class":"text"})
        img_item = img_item.find("img")
        img_item = img_item.attrs["src"]
        if not img_item:
            continue
        
        pos = img_item.rfind(".gif")
        if pos > 0:
            img_item = item.find("img").attrs["org_src"]
            if not img_item:
                continue
        
        file_name = "jiandan_" + str(index)
        file_path = os.path.join(".\\jiandan_pic", file_name)
        content = urlopen("http:" + img_item).read()
        if not content:
            continue
        imgtype = imghdr.what('', h = content)
        if not imgtype:
            continue

        with open(file_path + "." + imgtype, "wb") as picfile:
            picfile.write(content)

        index = index + 1

    if not stop:
        next_url = bsObj.find("div", {"class":"cp-pagenavi"}).find("a", {"class":"previous-comment-page"}).attrs["href"]
        if not next_url:
            break
    else:
        break