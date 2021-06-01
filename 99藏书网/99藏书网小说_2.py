import requests
from lxml import etree
from fake_useragent import FakeUserAgent
import base64
import time
import re


class Spider:
    def __init__(self):
        self.headers = {
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

    def get_html(self, url):
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.content.decode('utf-8')
        return None

    def get_data(self, tree):
        if tree is None:
            return None
        meta = [int(i) for i in self.get_meta(tree)]
        text = self.get_text(tree)
        if len(meta) != len(text) - 1:
            return None
        result = ['' for _ in meta]
        x = 0
        for i, j in enumerate(meta):
            if j < 3:
                result[j] = text[i + 1]
                x += 1
            else:
                result[j - x] = text[i + 1]
                x += 2
        return result

    @staticmethod
    def get_meta(tree):
        meta = tree.xpath(".//meta[5]/@content")[0]
        if meta:
            data = base64.b64decode(meta).decode("ascii")
            return re.split(r'[A-Z]+%', data)
        return None

    @staticmethod
    def get_text(tree):
        if tree is None:
            return None
        content = [tree.xpath(".//div[@id='content']/h2/text()")[0]]
        content[1:1] = [i.text for i in tree.xpath(
            ".//div[@id='content']/div")]
        return content

    def run(self, url):
        html = self.get_html(url)
        tree = etree.HTML(html) if html else None
        data = self.get_data(tree)
        for i in data:
            print(i)


def main():
    url = input('输入网址：')
    if not re.findall(r'http://www.99csw.com/book/[0-9]+/[0-9]+.htm', url):
        print('网址格式错误！')
    else:
        start = time.time()
        spider = Spider()
        spider.run(url)
        print('程序运行时间：{:.6f}'.format(time.time() - start))


if __name__ == '__main__':
    main()
