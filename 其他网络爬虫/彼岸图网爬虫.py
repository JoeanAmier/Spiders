import os
import random
import re
import time

import requests
import xlwt
from bs4 import BeautifulSoup
from fake_useragent import FakeUserAgent


def get_url(num):
    url_list = []
    for i in range(num):
        if i == 0:
            url = 'http://pic.netbian.com/'
        else:
            url = 'http://pic.netbian.com/index_' + str(i + 1) + '.html'
        url_list.append(url)
    return url_list


def get_html(url):
    header = {'user-agent': FakeUserAgent().chrome}
    if isinstance(url, list):
        all_html = ''
        for i in url:
            html = requests.get(url=i, headers=header)
            html = BeautifulSoup(html.content, 'html.parser')
            html = html.findAll('ul', class_="clearfix")
            all_html += str(html)
        return all_html
    elif isinstance(url, str):
        html = requests.get(url=url, headers=header)
        html = BeautifulSoup(html.content, 'html.parser')
        html = str(html)
        return html
    else:
        raise KeyError('我也不知道哪里错了')


def deal_data(html):
    data_list = []
    findurl = re.compile(r'href="(.*?)"')
    finddata = re.compile(
        r'<div class=".*?"><a href="" id=".*?"><img alt=".*?" data-pic=".*?" src="(.*?)" title="(.*?)"/></a></div>')
    url = re.findall(findurl, html)
    for i in range(len(url)):
        cache = []
        url[i] = 'http://pic.netbian.com/' + url[i]
        html = get_html(url[i])
        data = re.findall(finddata, html)
        cache.append('http://pic.netbian.com' + data[0][0])
        cache.append(data[0][1])
        data_list.append(cache)
    return data_list


def sava_xlsx(data):
    book = xlwt.Workbook(encoding='utf-8')
    sheet = book.add_sheet('爬取结果')
    tap = ('图片链接', '关键字')
    for i in range(2):
        sheet.write(0, i, tap[i])  # 添加列标签
    for i in range(len(data)):
        tap = data[i]
        if len(data) >= 100:
            print('\r', end='')
            print('正在保存数据到表格: {:.2f}%'.format(
                ((i + 1) / len(data)) * 100), '▉' * ((i + 1) // (len(data) // 50)), end='')
        elif len(data) > 0:
            print('\r', end='')
            print('正在保存数据到表格: {:.2f}%'.format(
                ((i + 1) / len(data)) * 100), '▉' * ((i + 1) * 50 // (len(data))), end='')
        else:
            print('出现错误')
        for j in range(2):
            data_1 = tap[j]
            sheet.write(i + 1, j, data_1)
    book.save('图片爬虫2.xlsx')
    print('\n')


def sava_path(data):
    root = os.getcwd() + '\\图片爬虫2\\'
    header = {'user-agent': FakeUserAgent().chrome}
    repeat = 0
    for index, item in enumerate(data):
        url = str(item[0])
        path = root + url.split('/')[-1]
        if len(data) >= 100:
            print('\r', end='')
            print('正在下载图片: {:.2f}%'.format(((index + 1) / len(data)) * 100),
                  '▉' * ((index + 1) // (len(data) // 50)),
                  end='')
        else:
            print('\r', end='')
            print('正在下载图片: {:.2f}%'.format(((index + 1) / len(data)) * 100),
                  '▉' * ((index + 1) * 50 // (len(data))),
                  end='')
        try:
            if not os.path.exists(root):  # 判断根目录是否存在
                os.mkdir(root)  # 创建根目录
            if not os.path.exists(path):  # 判断文件是否存在
                file = requests.get(url=url, headers=header)  # 请求文件
                time.sleep(random.randrange(2, 5, 1))
                with open(path, 'wb') as save:
                    save.write(file.content)
                    save.close()
            else:
                repeat += 1
        except BaseException:
            print('\n保存失败')
    print('\n重复图片：' + str(repeat) + '张')


def main():
    num = int(input('爬取页数(1 ~ 1250)：'))
    if num < 1 or num > 1250:
        raise ValueError('页数输入错误')
    url = get_url(num)
    html = get_html(url)
    data = deal_data(html)
    sava_xlsx(data)
    sava_path(data)
    print('程序结束')


if __name__ == '__main__':
    main()
