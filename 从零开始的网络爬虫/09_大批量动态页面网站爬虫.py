import sqlite3
import time
import requests


def get_html(template):
    html = []
    """
    示例代码仅爬取前三页数据
    """
    for page in range(3):
        url = template.format(page * 18)
        response = open_url(url)
        html.append(response)
    return html


def open_url(url):
    response = requests.get(url)
    return response.json()


def get_data(html):
    data = []
    for page in html:
        for item in page['results']:
            movie = []
            id = item['id']
            name = item['name']
            authors = item['authors']
            score = item['score']
            movie.append(id)
            movie.append(name)
            if authors:
                cache = ''.join(i.replace('\n', '').strip() for i in authors)
                movie.append(cache)
            else:
                movie.append(authors)
            movie.append(score)
            data.append(movie)
    return data


def save_data(data):
    sqlite = sqlite3.connect('网络爬虫数据库.db')
    cursor = sqlite.cursor()
    sql = '''create table 大批量动态页面网站爬虫
    ('ID' text primary key not null,
    '名称' text not null,
    '作者' text,
    '评分' text not null)'''
    try:
        cursor.execute(sql)
        sqlite.commit()
    except sqlite3.OperationalError:
        print('数据表已存在')
    for item in data:
        for index in range(len(item)):
            item[index] = '"' + str(item[index]) + '"'
        sql = '''insert into 大批量动态页面网站爬虫
        values(%s)''' % ', '.join(item)
        cursor.execute(sql)
    sqlite.commit()
    sqlite.close()


def main():
    """
    真实网址：https://spa5.scrape.center/
    图书网站，无反爬，数据通过 Ajax 加载，有翻页，适合大批量动态页面渲染抓取。
    代码测试时间：2021/3/20
    """
    url = 'https://spa5.scrape.center/api/book/?limit=18&offset={}'
    start = time.time()
    html = get_html(url)
    data = get_data(html)
    save_data(data)
    print('运行时间：{:.6f}'.format(time.time() - start))


if __name__ == '__main__':
    main()
