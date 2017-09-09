import urllib
from urllib.request import urlopen

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import requests

import re
import os
import imghdr
import time



def init_dir(dirname):
    if not os.path.exists(dirname):
        os.mkdir(dirname)
    else:
        for f in os.listdir(dirname):
            path = os.path.join(dirname, f)
            os.remove(path)

def login(driver):
    login_url = "https://www.zhihu.com/#signin"
    driver.get(login_url)
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//input[@type='password']")))
    driver.find_element_by_xpath("//input[@type='text]").send_keys("18666219953")
    driver.find_element_by_xpath("//input[@type='password]").send_keys("5555YDYHHGXX")
    driver.find_element_by_xpath("//button[@type='submit']").click()
    time.sleep(3)


def crawl_pages(driver, save_path):
    target_url = "https://www.zhihu.com/question/37787176"
    driver.get(target_url)
    time.sleep(3)
    bsObj = BeautifulSoup(driver.page_source, "html.parser")
    imgs = bsObj.findAll("img", {"src":re.compile("(jpg|jpeg|png)$")})
    index = 1
    for img in imgs:
        img_url = img.attrs["src"]
        file_name = "zhihu_" + str(index)
        content = urlopen(img_url).read()
        if not content:
            continue
        imgtype = imghdr.what('', h = content)
        if not imgtype:
            continue
        save_pic(content, save_path, file_name, imgtype)
        print("img " + str(index) + " finished")
        index = index + 1

def save_pic(content, path, filename, filetype):
    file_path = os.path.join(path, filename)
    with open(file_path + "." + filetype, "wb") as picfile:
        picfile.write(content)




driver = webdriver.PhantomJS(executable_path = '../phantomjs/bin/phantomjs.exe')

init_dir("./zhihu_pic")
#login(driver)
crawl_pages(driver, "./zhihu_pic")

driver.close()