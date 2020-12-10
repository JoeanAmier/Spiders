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
            name = page['results'][item]['name']
            alias = page['results'][item]['alias']
            categories = page['results'][item]['categories']
            regions = page['results'][item]['regions']
            minute = page['results'][item]['minute']
            published_at = page['results'][item]['published_at']
            score = page['results'][item]['score']
            movie.append(name)
            movie.append(alias)
            movie.append('%s' % ' '.join(categories))
            movie.append('%s' % ' '.join(regions))
            movie.append(str(minute) + ' 分钟')
            movie.append(published_at)
            movie.append(score)
            data.append(movie)
    return data


def save_data(data):
    sqlite = sqlite3.connect('网络爬虫数据库.db')
    cursor = sqlite.cursor()
    sql = '''create table 无页码翻页网站爬虫
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
        sql = '''insert into 无页码翻页网站爬虫
        values(%s)''' % ', '.join(item)
        cursor.execute(sql)
    sqlite.commit()
    sqlite.close()


def main():
    """
    真实网址：https://spa3.scrape.center/
    电影数据网站，无反爬，数据通过 Ajax 加载，无页码翻页，下拉至底部刷新，适合 Ajax 分析和动态页面渲染爬取。
    与爬取异步加载网站方法相同
    分析 Ajax 请求，通过 Ajax 请求直接获取 json 格式的网页数据
    下面的 url 是分析 Ajax 请求后得到的网络地址
    offset 参数代表页数，规律是：offset = (页数 - 1) * 10
    代码测试时间：2020/12/10
    """
    url = 'https://spa3.scrape.center/api/movie/?limit=10&offset='
    start = time.time()
    html = get_html(url)
    data = get_data(html)
    save_data(data)
    print('运行时间：{:.6f}'.format(time.time() - start))


if __name__ == '__main__':
    main()
