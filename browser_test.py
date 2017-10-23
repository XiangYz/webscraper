import requests
from bs4 import BeautifulSoup
import os
from selenium import webdriver

'Mozilla/5.0 (iPhone; CPU iPhone OS 7_1_2 like Mac OS X) AppleWebKit/537.51.2 (KHTML, likeGecko) Version/7.0 Mobile/11D257 Safari/9537.53'

"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5)AppleWebKit 537.36 (KHTML, like Gecko) Chrome"

session = requests.Session()
headers = {
    "User-Agent":'Mozilla/5.0 (iPhone; CPU iPhone OS 7_1_2 like Mac OS X) AppleWebKit/537.51.2 (KHTML, likeGecko) Version/7.0 Mobile/11D257 Safari/9537.53',
    "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
}
url = "https://www.whatismybrowser.com/developers/what-http-headers-is-my-browser-sending"
req = session.get(url, headers = headers)
bsobj = BeautifulSoup(req.text, "html.parser")
#print(bsobj.find("table", {"class":"table-striped"}).get_text())



driver = webdriver.PhantomJS(executable_path = '../phantomjs/bin/phantomjs.exe')
driver.get("http://pythonscraping.com")
driver.implicitly_wait(1)
print(driver.get_cookies())

savedCookies = driver.get_cookies()

driver2 = webdriver.PhantomJS(executable_path = '../phantomjs/bin/phantomjs.exe')
driver2.get("http://pythonscraping.com")
driver2.implicitly_wait(1)
print(driver2.get_cookies())
driver2.delete_all_cookies()
for cookie in savedCookies:
    driver2.add_cookie(cookie)

driver2.get("http://pythonscraping.com")
drver2.implicitly_wait(1)
print(driver2.get_cookies())