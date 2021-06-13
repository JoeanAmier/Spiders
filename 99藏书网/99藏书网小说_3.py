import requests
from lxml import etree
from fake_useragent import FakeUserAgent
import time
import re
import base64


def get_meta(url):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Host': 'www.99csw.com',
        'Pragma': 'no-cache',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': FakeUserAgent().chrome}
    response = requests.get(url, headers=headers)
    tree = etree.HTML(response.content)
    return tree.xpath('//meta[5]/@content')[0]


def decrypt(text):
    data = base64.b64decode(text).decode("ascii")
    return [int(i) for i in re.split(r'[A-Z]+%', data)]


def get_data(text):
    data = []
    i = 0
    for j in text:
        if j < 3:
            data.append(j)
            i += 1
        else:
            data.append(j - i)
            i += 2
    return data


def main():
    url = input('输入网址：')
    start = time.time()
    meta = get_meta(url)
    data = get_data(decrypt(meta))
    print(data)
    print('程序运行时间：{:.6f}'.format(time.time() - start))


if __name__ == '__main__':
    main()
