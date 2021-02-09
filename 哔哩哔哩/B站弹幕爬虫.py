import requests
from bs4 import BeautifulSoup
import re
from fake_useragent import FakeUserAgent
import json
import jieba
import wordcloud


def input_url():
    url = input('输入视频网址：')
    if url[-1] != '/':
        url += '/'
    else:
        pass
    check_url = re.compile(r'^https://www.bilibili.com/video/(.*?)/$')
    bv = re.findall(check_url, url)
    if bool(bv):
        if len(bv[0].split('/')) == 1:
            return bv[0]
        else:
            raise ValueError('视频网址输入错误')


def get_url(bv):
    content, text = open_url(
        'https://api.bilibili.com/x/player/pagelist?bvid={}&jsonp=jsonp'.format(bv))
    text = json.loads(text)
    av = text['data'][0]['cid']
    html = 'http://comment.bilibili.com/' + str(av) + '.xml'
    return html


def open_url(url):
    header = {'user-agent': FakeUserAgent().chrome}
    html = requests.get(url=url, headers=header)
    return html.content, html.text


def deal_data(html):
    find = re.compile(r'<d p=".*?">(.*?)</d>')
    data = ''
    html = BeautifulSoup(html, 'html.parser')
    for item in html.findAll('d'):
        item = str(item)
        item = re.findall(find, item)
        data += item[0]
    return data


def cloud(data):
    data = jieba.cut(data)
    word = wordcloud.WordCloud(
        font_path='msyh.ttc',
        background_color='white',
        width=1920,
        height=1080)
    word.generate('%s' % ' '.join(data))
    word.to_file('弹幕词云图.png')


def main():
    url = input_url()
    url = get_url(url)
    content, text = open_url(url)
    data = deal_data(content)
    cloud(data)


if __name__ == '__main__':
    main()
