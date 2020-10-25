import sqlite3
import time
import requests
import json


def get_html(template):
    html = []
    for page in range(0, 10):
        url = template + str(page * 10)
        response = open_url(url)
        html.append(response)
    return html


def open_url(url):
    response = requests.get(url)
    return response.content.decode('utf-8')


def get_data(html):
    data = []
    for pages in html:
        for item in range(0, 10):
            movie = []
            page = json.loads(pages)
            title = page['results'][item]['title']
            url = page['results'][item]['url']
            movie.append(title)
            movie.append(url)
            data.append(movie)
    return data


def save_data(data):
    sqlite = sqlite3.connect('网络爬虫数据库.db')
    cursor = sqlite.cursor()
    sql = '''create table 异步智能网页网站爬虫
    ('标题' text primary key not null,
    '链接' text not null)'''
    try:
        cursor.execute(sql)
        sqlite.commit()
    except sqlite3.OperationalError:
        print('数据表已存在')
    for item in data:
        for index in range(len(item)):
            item[index] = '"' + str(item[index]) + '"'
        sql = '''insert into 异步智能网页网站爬虫
        values(%s)''' % ', '.join(item)
        try:
            cursor.execute(sql)
        except BaseException:
            continue
    sqlite.commit()
    sqlite.close()


def main():
    """
    真实网址：https://spa4.scrape.center/
    电影数据网站，无反爬，数据通过 Ajax 加载，无页码翻页，下拉至底部刷新，适合 Ajax 分析和动态页面渲染爬取。
    与爬取异步加载网站方法相同
    分析 Ajax 请求，通过 Ajax 请求直接获取 json 格式的网页数据
    下面的 url 是分析 Ajax 请求后得到的网络地址
    offset 参数代表页数，规律是：offset = (页数 - 1) * 10
    """
    url = 'https://spa4.scrape.center/api/news/?limit=10&offset='
    start = time.time()
    html = get_html(url)
    data = get_data(html)
    save_data(data)
    print('运行时间：{:.6f}'.format(time.time() - start))


if __name__ == '__main__':
    main()
