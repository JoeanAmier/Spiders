import requests
from bs4 import BeautifulSoup
import re
from fake_useragent import FakeUserAgent
import time
import random
from pymongo import MongoClient


def get_url(keyword, pages):
    url_list = []
    while pages >= 1 and pages <= 100:
        if pages == 1:
            url = 'https://search.jd.com/Search?keyword={}&wq={}'.format(
                keyword, keyword)
            pages -= 1
        else:
            url = 'https://search.jd.com/Search?keyword={}&wq={}&page={}'.format(
                keyword, keyword, pages * 2 - 1)
            pages -= 1
        url_list.append(url)
    if len(url_list) != 0:
        url_list.reverse()
        return url_list
    else:
        raise ValueError('页数输入错误')


def goto_url(url_list):
    header = {'user-agent': str(FakeUserAgent().chrome)}
    all_html = ''
    for i in range(len(url_list)):
        html = requests.get(url=url_list[i], headers=header)
        time.sleep(random.randrange(3, 7, 1))
        if len(url_list) >= 100:
            print('\r', end='')
            print('正在获取数据: {:.2f}%'.format(((i + 1) / len(url_list)) * 100),
                  '▉' * ((i + 1) // (len(url_list) // 50)),
                  end='')
        else:
            print('\r', end='')
            print('正在获取数据: {:.2f}%'.format(((i + 1) / len(url_list)) * 100),
                  '▉' * ((i + 1) * 50 // (len(url_list))),
                  end='')
        html = html.content.decode('utf-8')
        all_html += html
    print('')
    return all_html


def get_data(html):
    findurl = re.compile(r'<a href="(.*)" onclick="searchlog.*"')
    data = BeautifulSoup(html, 'html.parser')
    url_list = []
    for item in data.findAll('li', class_='gl-item'):
        item = str(item)
        url = re.findall(findurl, item)
        if len(url) == 3:
            url = 'https:' + url[0]
            url_list.append(url)
        else:
            raise IndexError('获取链接发生错误')
    debug = input('是否获取全部数据？\n获取全部数据直接回车，只获取前5条数据请输入任意字符后回车')
    if len(debug) == 0:
        pass
    else:
        del url_list[5:]
    print('获取商品数量：', len(url_list))
    return url_list


def deal_data(data):
    findbrand = re.compile(r'<li title=".*?">(.*?)： <a.*?>(.*?)</a>')
    findinfo = re.compile(r'<li title=".*?">(.*?)：(.*?)</li>')
    data_list = []
    data = BeautifulSoup(data, 'html.parser')
    for item in data.findAll('div', class_='p-parameter'):
        cache = []
        for info in item.findAll('ul', class_='parameter2 p-parameter-list'):
            info = str(info)
            info = re.findall(findinfo, info)
            for index in range(len(info)):
                cache.append(info[index])
        item = str(item)
        brand = re.findall(findbrand, item)
        cache.insert(0, brand[0])
        data_list.append(cache)
    return data_list


def save_data(data):
    conn = MongoClient('mongodb://localhost:27017/')
    db = conn.JDdatabase
    list = []
    for i in data:
        info = {}
        for j in i:
            info[j[0]] = j[1]
        list.append(info)
    for i, j in enumerate(list):
        try:
            db.col.insert_one(j)
        except BaseException:
            raise ValueError(j)


def main():
    kw = input('搜索关键字：')
    pages = int(input('爬取页数：'))
    html = get_url(kw, pages)
    html = goto_url(html)
    data = get_data(html)
    data = goto_url(data)
    data = deal_data(data)
    save = input('是否保存数据？\n保存全部数据到Mongo数据库直接回车，不保存数据请输入任意字符后回车（获取数据后直接输出）')
    if bool(save):
        save_data(data)
    else:
        print(data)
    print('程序结束')


if __name__ == '__main__':
    print('需要安装Mongo数据库，获取数据时未处理异步加载内容')
    main()
