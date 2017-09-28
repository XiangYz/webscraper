import urllib
from urllib.request import urlopen
from bs4 import BeautifulSoup
from selenium import webdriver
import re
import os
import imghdr
import time
import requests


def clear_dir():
    if not os.path.exists("./zhihu_pic"):
        os.mkdir("zhihu_pic")
    else:
        for f in os.listdir("./zhihu_pic"):
            path = os.path.join("./zhihu_pic", f)
            os.remove(path)


headers = {
    'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding' : 'gzip, deflate, sdch, br',
    'Connection' : 'keep-alive',
    'DNT' : '1',
    'Host' : 'www.zhihu.com',
    'Upgrade-Insecure-Requests' : '1',
    'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
}

session = requests.Session()


def login():

    login_page = session.get("https://www.zhihu.com/login/phone_num", headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}).text
    login_page_bs = BeautifulSoup(login_page, "html.parser")
    xsrf = login_page_bs.find("input", {"name":"_xsrf"}).attrs['value']


    params = {
        '_xsrf':xsrf,
        'password':'5555YDYHHGXX',
        'captcha_type':'cn',
        'phone_num':'18666219953',
    }

    #session.headers = headers
    r = session.post("https://www.zhihu.com/login/phone_num", data = params)
    return r

print(login())

my_page = session.get("https://www.zhihu.com/people/Xiangyuzhe/following")
my_page_bs = BeautifulSoup(my_page.text, "html.parser")
num_of_I_following = int(my_page_bs.find("div", {"class":"NumberBoard-value"}).text)
print(num_of_I_following)


'''
res = session.get("https://www.zhihu.com/question/37787176", headers = headers)
bsObj = BeautifulSoup(res.text, "html.parser")
#print(bsObj)
imgs = bsObj.findAll("img", {"src":re.compile("(jpg|jpeg|png)$")})
index = 1
for img in imgs:
    img_url = img.attrs["src"]
    file_name = "zhihu_" + str(index)
    file_path = os.path.join("./zhihu_pic", file_name)
    content = urlopen(img_url).read()
    if not content:
        continue
    imgtype = imghdr.what('', h = content)
    if not imgtype:
        continue

    with open(file_path + "." + imgtype, "wb") as picfile:
        picfile.write(content)

    print("img " + str(index) + " finished")
    index = index + 1
'''

