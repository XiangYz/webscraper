from selenium import webdriver
from bs4 import BeautifulSoup
import time


driver = webdriver.PhantomJS(executable_path = '../phantomjs/bin/phantomjs.exe')
driver.get("http://pythonscraping.com/pages/javascript/ajaxDemo.html")
time.sleep(3)
pageSrc = driver.page_source
bsObj = BeautifulSoup(pageSrc, "html.parser")
txt = bsObj.find("div", {"id":"content"}).get_text()
#print(driver.find_element_by_id("content").text)
print(txt)
driver.close()