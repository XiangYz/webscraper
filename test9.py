import requests

params = {"firstname":"Ryan", "lastname":"Mitchell"}
file = {'uploadFile':open('c:/jiandan_pic/jiandan_6.jpeg', 'rb')}
#r = requests.post("http://pythonscraping.com/files/processing.php", data = params)
r = requests.post('http://pythonscraping.com/pages/processing2.php', files = file)
print(r.text)