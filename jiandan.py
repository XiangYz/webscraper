import urllib.request
from bs4 import BeautifulSoup
import re
import os
import imghdr
import time



user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'  
headers = { 'User-Agent' : user_agent }  





index = 1
stop = False
next_url = "http://jandan.net/ooxx"



if not os.path.exists(".\\jiandan_pic"):
    os.mkdir("jiandan_pic")

while True:

    webRequest = urllib.request.Request(next_url, headers=headers)
    html = urllib.request.urlopen(webRequest)

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
            if int(days) >= 2:
                stop = True
                break
        
        img_item = item.find("div", {"class":"row"})
        print(img_item)
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
        content = urllib.urlopen("http:" + img_item).read()
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