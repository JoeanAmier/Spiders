import sqlite3
import requests
import time
from bs4 import BeautifulSoup
import re


def open_url(url):
    pass


def get_data(url):
    pass


def save_data(data):
    sqlite = sqlite3.connect('网络爬虫数据库.db')
    cursor = sqlite.cursor()
    sql = '''create table 动态页面渲染网站爬虫
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
        sql = '''insert into 动态页面渲染网站爬虫
        values(%s)''' % ', '.join(item)
        cursor.execute(sql)
    sqlite.commit()
    sqlite.close()


def main():
    url = 'https://spa2.scrape.center/'
    """电影数据网站，无反爬，数据通过 Ajax 加载，数据接口参数加密且有时间限制
    适合动态页面渲染爬取或 JavaScript 逆向分析。"""
    start = time.time()
    data = get_data(url)
    save_data(data)
    print('运行时间：{:.6f}'.format(time.time() - start))


if __name__ == '__main__':
    main()
