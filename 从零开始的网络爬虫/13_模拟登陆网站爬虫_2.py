import re
import sqlite3
import time

import requests
from bs4 import BeautifulSoup


def get_html(url):
    data = {'username': 'admin', 'password': 'admin'}
    response = requests.post(url, data=data, allow_redirects=False)
    cookie = response.cookies
    html = ''
    for page in range(1, 11):
        url = 'https://login2.scrape.center/page/' + str(page)
        response = open_url(cookie, url)
        html += response
    return html


def open_url(cookie, url):
    response = requests.get(url, cookies=cookie)
    return response.text


def get_data(html):
    findname = re.compile(
        r'<h2 class=".*?" data-v-7f856186=".*?">(.*?) - (.*?)</h2>')
    findtype = re.compile(
        r'<button class=".*?" data-v-7f856186=".*?" type_="button">\n<span>(.*?)</span>')
    findinfo = re.compile(
        r'<span data-v-7f856186="">(.*?)</span>\n<.*?> / </span>\n<span data-v-7f856186="">(.*?)</span>')
    findpublished = re.compile(
        r'<div class="m-v-sm info" data-v-7f856186="">\n<span data-v-7f856186="">(.*?) 上映</span>')
    findscore = re.compile(
        r'<p class="score m-t-md m-b-n-sm" data-v-7f856186="">\n(.*?)</p>')
    html = BeautifulSoup(html, 'lxml')
    data = []
    for item in html.findAll('div', class_='el-card__body'):
        item = str(item)
        movie = []
        chinese_name = re.findall(findname, item)[0][0]
        english_name = re.findall(findname, item)[0][1]
        type_ = ''.join(i + ' ' for i in re.findall(findtype, item))
        country = re.findall(findinfo, item)[0][0]
        time_ = re.findall(findinfo, item)[0][1]
        published = re.findall(findpublished, item)
        published = published[0] if len(published) == 1 else None
        score = re.findall(findscore, item)[0].strip()
        movie.append(chinese_name)
        movie.append(english_name)
        movie.append(type_.strip())
        movie.append(country)
        movie.append(time_)
        movie.append(published)
        movie.append(score)
        data.append(movie)
    return data


def save_data(data):
    sqlite = sqlite3.connect('网络爬虫数据库.db')
    cursor = sqlite.cursor()
    sql = '''create table 模拟登陆网站爬虫
    ('中文名称' text primary key not null,
    '其他名称' text not null,
    '类型' text not null,
    '国家' text not null,
    '时长' text not null,
    '上映' date,
    '评分' text)'''
    try:
        cursor.execute(sql)
        sqlite.commit()
    except sqlite3.OperationalError:
        print('数据表已存在')
    for item in data:
        for index in range(len(item)):
            item[index] = '"' + str(item[index]) + '"'
        sql = '''insert into 模拟登陆网站爬虫
        values(%s)''' % ', '.join(item)
        cursor.execute(sql)
    sqlite.commit()
    sqlite.close()


def main():
    url = 'https://login2.scrape.center/login?next=/'
    """
    对接 Session + Cookies 模拟登录，适合用作 Session + Cookies 模拟登录练习。
    代码测试时间：2021/3/25
    """
    start = time.time()
    html = get_html(url)
    data = get_data(html)
    save_data(data)
    print('运行时间：{:.6f}'.format(time.time() - start))


if __name__ == '__main__':
    main()
