import itchat

itchat.login()

friends = itchat.get_friends(update = True)[0:]
info = {}
for i in friends:
    info[i['NickName']] = i.Signature

print(info)