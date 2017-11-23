import base64
import pyDes
import binascii
import requests

local_key = b"\x40\x62\x7F\xB5\x89\x52\xFE\x07"
on_page = b"35B868223729B22C39B50981EE563DC8"
on_page_bytes = binascii.unhexlify(on_page)
passwd = b"wb6824247"
passwd = passwd + b"\x00\x00\x00\x00\x00\x00\x00"
#print(passwd)
des_dec = pyDes.des(local_key, pyDes.ECB)
dec_res = des_dec.decrypt(on_page_bytes)
#print(dec_res)
dec_res = binascii.unhexlify(dec_res)
#print(dec_res)
des_enc = pyDes.des(dec_res, pyDes.ECB)
res = des_enc.encrypt(passwd)
res = binascii.hexlify(res)
print(res)



s = requests.Session()
headers = {"Accept":"*/*",
    "Accept-Encoding":"gzip, deflate",
    "Accept-Language":"zh-CN",
    "User-Agent":"Mozilla/5.0(compatible;MSIE 9.0; Windows NT 6.1; Trident/7.0)",
    "X-Requested-With":"XMLHttpRequest"}
params = {"ywdm":"A01",
    "parm":"login",
    "iptPassword":res,
    "clientCert":"",
    "clientSigdata":"",
    "randomKey":on_page,
    "unitKind":"",
    "random":"61175772",
    "checkCA":"A",
    "hid":"",
    "upm021":"",
    "authorizationNum":"",
    "iptPhoneVerificationCode":"",
    "iptUserId":"231004198206100011"
    }
s.get("https://www.renshenet.org.cn/sionline/loginControler", headers = headers)
print(s)
#s.post("https://www.renshenet.org.cn/sionline/loginControler", params = params)
#print(s)