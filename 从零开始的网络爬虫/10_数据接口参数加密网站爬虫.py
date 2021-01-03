import sqlite3
import time
import requests
import json


def get_html(template):
    html = []
    for page in range(0, 10):
        token = open_url('http://127.0.0.1:3000/')
        url = template.format(str(page * 10), token)
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
    sql = '''create table 数据接口参数加密网站爬虫
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
        sql = '''insert into 数据接口参数加密网站爬虫
        values(%s)''' % ', '.join(item)
        cursor.execute(sql)
    sqlite.commit()
    sqlite.close()


def main():
    """
    真实网址：https://spa6.scrape.center/
    电影数据网站，数据通过 Ajax 加载，数据接口参数加密且有时间限制，源码经过混淆
    适合 JavaScript 逆向分析
    使用 06_动态页面渲染网站爬虫.js 获取加密参数
    代码测试时间：2021/1/2
    """
    url = 'https://spa6.scrape.center/api/movie/?limit=10&offset={}&token={}'
    start = time.time()
    html = get_html(url)
    data = get_data(html)
    save_data(data)
    print('运行时间：{:.6f}'.format(time.time() - start))


if __name__ == '__main__':
    main()
