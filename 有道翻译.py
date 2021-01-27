import requests
import hashlib
import time
import random


class YouDao:
    """可供调用"""

    def __init__(self):
        self.cookie = self.get_cookie()

    def get_cookie(self):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,applicat'
                      'ion/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Host': 'fanyi.youdao.com',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/8'
                          '7.0.4280.141 Safari/537.36 Edg/87.0.664.75'
        }
        response = requests.get('http://fanyi.youdao.com/', headers=headers)
        cookie = [i.name + '=' + i.value for i in response.cookies]
        return cookie

    def get_data(self, key):
        url = 'http://fanyi.youdao.com/translate_o?smartresult=dict&smartresult=rule'
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            'Cookie': '%s' % ','.join(self.cookie),
            "DNT": "1",
            "Host": "fanyi.youdao.com",
            "Origin": "http://fanyi.youdao.com",
            "Pragma": "no-cache",
            "Referer": "http://fanyi.youdao.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chro"
                          "me/87.0.4280.141 Safari/537.36 Edg/87.0.664.75",
            "X-Requested-With": "XMLHttpRequest"
        }
        lts = str(int(time.time() * 1000))
        salt = lts + str(random.randint(0, 10))
        sign = self.get_sign(key, salt)
        form = {'i': key,
                'from': 'AUTO',
                'to': 'AUTO',
                'smartresult': 'dict',
                'client': 'fanyideskweb',
                'salt': salt,
                'sign': sign,
                'lts': lts,
                'bv': '02c2dd94fb562b4304f9b0c657990444',
                'doctype': 'json',
                'version': '2.1',
                'keyfrom': 'fanyi.web',
                'action': 'FY_BY_REALTlME'}
        response = requests.post(url=url, headers=headers, params=form)
        data = response.json()
        print('翻译结果：', data['translateResult'][0][0]['tgt'])
        print('来自有道词典结果：')
        for i in data['smartResult']['entries']:
            if i:
                print(i.replace('\r\n', ''))
            else:
                continue

    def get_sign(self, key, salt):
        sign = "fanyideskweb" + key + salt + "Tbh5E8=q6U3EXe+&L[4c@"
        data = hashlib.md5()
        data.update(sign.encode('utf-8'))
        return data.hexdigest()

    def translate(self, key):
        self.get_data(key) if key else print('翻译内容为空')


def main():
    key = input('翻译内容：')
    YouDao().translate(key)


if __name__ == '__main__':
    main()
