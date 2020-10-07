import requests
from fake_useragent import FakeUserAgent
import chardet
from bs4 import BeautifulSoup
from urllib import parse


class UrlManager():
    def __init__(self):
        self.new_urls = set()
        self.old_urls = set()

    def new_url_size(self):
        """返回未爬取网址数量"""
        return len(self.new_urls)

    def old_url_size(self):
        """返回已爬取网址数量"""
        return len(self.old_urls)

    def has_new_url(self):
        """判断有无未爬取网址"""
        return self.new_url_size() != 0

    def get_new_url(self):
        """获取一个待爬取网址"""
        new_url = self.new_urls.pop()
        self.old_urls.add(new_url)
        return new_url

    def add_new_url(self, url):
        """添加待爬取单个网址"""
        if url is None:
            return None
        if url not in self.new_urls and url not in self.old_urls:
            self.new_urls.add(url)

    def add_new_urls(self, urls):
        """添加待爬取多个网址"""
        if urls is None or len(urls) == 0:
            return None
        else:
            for url in urls:
                self.add_new_url(url)


class HtmlDownloader():
    def __init__(self):
        self.header = {'user-agent': FakeUserAgent().chrome}

    def download(self, url):
        if url is None:
            return None
        response = requests.get(url, headers=self.header)
        if response.status_code == 200:
            return response.content.decode(
                chardet.detect(response.content)['encoding'])
        else:
            return None


class HtmlParser():
    def parser(self, url, html):
        if url is None or html is None:
            return
        soup = BeautifulSoup(html, 'lxml')
        new_urls = self._get_new_url(url, soup)
        new_data = self._get_new_data(url, soup)
        return new_urls, new_data

    def _get_new_url(self, url, soup):
        new_urls = set()
        links = soup.select('div.basic-info.cmn-clearfix a')
        if bool(links):
            for item in links:
                new_url = parse.urljoin(url, item['href'])
                new_urls.add(new_url)
        return new_urls

    def _get_new_data(self, url, soup):
        new_data = [url]
        info = soup.select('div.lemma-summary > div.para')
        title = soup.select('.lemmaWgt-lemmaTitle-title > h1')
        if bool(info) and bool(title):
            new_data.append(title[0].text)
            new_data.append(info[0].text)
            return new_data
        return None


class DataOutput():
    def __init__(self):
        self.datas = []

    def store_data(self, data):
        if data is None:
            return
        self.datas.append(data)

    def output_file(self):
        with open('百度百科爬虫结果.txt', 'w+', encoding='utf-8') as file:
            for item in self.datas:
                file.write('%s' % ','.join(item))
                file.write('\n')


class SpiderMan():
    def __init__(self):
        self.manager = UrlManager()
        self.downloader = HtmlDownloader()
        self.parser = HtmlParser()
        self.output = DataOutput()

    def crawl(self, root_url):
        self.manager.add_new_url(root_url)
        while (self.manager.new_url_size()
               and self.manager.old_url_size() <= 100):
            new_url = self.manager.get_new_url()
            html = self.downloader.download(new_url)
            new_urls, new_data = self.parser.parser(new_url, html)
            self.manager.add_new_urls(new_urls)
            self.output.store_data(new_data)
        self.output.output_file()


if __name__ == '__main__':
    spider = SpiderMan()
    spider.crawl(
        'https://baike.baidu.com/item/%E8%8F%B2%E5%BE%8B%E5%AE%BE%E5%B8%98%E8%9B%A4')
