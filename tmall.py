# coding = utf-8

import urllib
from urllib.request import urlopen
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common import action_chains, keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from multiprocessing import Process, Pool, Queue
import re
import os
import imghdr
import time


url = "https://www.tmall.com"

#driver = webdriver.PhantomJS(executable_path = '../phantomjs/bin/phantomjs.exe')
driver = webdriver.Chrome("chromedriver.exe")

driver.get(url)

input_edit = WebDriverWait(driver, 3).until(
    EC.presence_of_element_located((By.XPATH, "//input[@id='mq']"))
)


'''
submit_btn = WebDriverWait(driver, 3).until(
    EC.presence_of_element_located((By.XPATH, "//button[@type='submit']"))
)
'''

submit_btn = WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.XPATH, "//button[@type='submit']"))
)

   

input_edit.clear()
input_edit.send_keys("男士T恤")
submit_btn.click()


btm_input_edit = WebDriverWait(driver, 3).until(
    EC.presence_of_element_located((By.XPATH, "//input[@id='btm-mq']"))
)


time.sleep(10)


driver.close()