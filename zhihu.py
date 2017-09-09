import urllib
from urllib.request import urlopen
from bs4 import BeautifulSoup
from selenium import webdriver
import re
import os
import imghdr
import time
import requests




if not os.path.exists("./zhihu_pic"):
    os.mkdir("zhihu_pic")
else:
    for f in os.listdir("./zhihu_pic"):
        path = os.path.join("./zhihu_pic", f)
        os.remove(path)


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) \
    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
}
session = requests.Session()

params = {'username':'18666219953', 'password':'5555YDYHHGXX'}
s = session.post("https://www.zhihu.com/#signin", params)

'''
print("Cookie is set to:")
print(s.cookies.get_dict())
print("---------")
print("Going to profile page...")
'''



s = session.get("https://www.zhihu.com/question/37787176", headers = headers)
bsObj = BeautifulSoup(s.text, "html.parser")
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


