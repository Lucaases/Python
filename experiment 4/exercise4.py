dic={'Alice': 11, 'Beth': 45, 'Cecil': 14}

def lookup(dic,value):
    new_dic = dict(zip(dic.values(),dic.keys()))
    return new_dic[value]

print(dic['Alice'],dic['Beth'],dic['Cecil'])
print(lookup(dic,11),lookup(dic,45),lookup(dic,14))