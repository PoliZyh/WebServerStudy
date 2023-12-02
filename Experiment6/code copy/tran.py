#coding=utf-8
from hashlib import md5
import random
import requests


# 调用百度翻译
def baiduTran(strs):
    appid = '20231009001841959' 
    appkey = 'RRqR2QPLbfN33Em6rtCx'

    from_lang = 'jp'
    to_lang =  'zh'

    endpoint = 'http://api.fanyi.baidu.com'
    path = '/api/trans/vip/translate'
    url = endpoint + path

    query = strs

    # Generate salt and sign
    def make_md5(s, encoding='utf-8'):
        return md5(s.encode(encoding)).hexdigest()

    salt = random.randint(32768, 65536)
    sign = make_md5(appid + query + str(salt) + appkey)

    # Build request
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {'appid': appid, 'q': query, 'from': from_lang, 'to': to_lang, 'salt': salt, 'sign': sign}

    # Send request
    r = requests.post(url, params=payload, headers=headers)
    res = r.json()

    res_str = ''

    for str_item in res['trans_result']:
        res_str += str_item['dst']

    return res_str