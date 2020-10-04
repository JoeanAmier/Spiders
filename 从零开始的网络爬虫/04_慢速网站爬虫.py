from bs4 import BeautifulSoup
import re
import sqlite3
import time
import requests


def get_html(url):
    template = url + 'page/'
    html = ''
    for page in range(1, 11):
        url = template + str(page)
        response = open_url(url)
        html += response
    return html


def open_url(url):
    response = requests.get(url, timeout=None)
    return response.text


def get_data(html):
    findname = re.compile(
        r'<h2 class=".*?" data-v-7f856186=".*?">(.*?) - (.*?)</h2>')
    findtype = re.compile(
        r'<button class=".*?" data-v-7f856186=".*?" type="button">\n<span>(.*?)</span>')
    findinfo = re.compile(
        r'<span data-v-7f856186="">(.*?)</span>\n<.*?> / </span>\n<span data-v-7f856186="">(.*?)</span>')
    findpublished = re.compile(
        r'<div class="m-v-sm info" data-v-7f856186="">\n<span data-v-7f856186="">(.*?) 上映</span>')
    findscore = re.compile(
        r'<p class="score m-t-md m-b-n-sm" data-v-7f856186="">\n(.*?)</p>')
    html = BeautifulSoup(html, 'html.parser')
    data = []
    for item in html.findAll('div', class_='el-card__body'):
        item = str(item)
        movie = []
        chinese_name = re.findall(findname, item)[0][0]
        english_name = re.findall(findname, item)[0][1]
        type = ''
        for i in re.findall(findtype, item):
            type += i + ' '
        country = re.findall(findinfo, item)[0][0]
        time = re.findall(findinfo, item)[0][1]
        published = re.findall(findpublished, item)
        if len(published) == 1:
            published = published[0]
        else:
            published = None
        score = re.findall(findscore, item)[0].strip()
        movie.append(chinese_name)
        movie.append(english_name)
        movie.append(type.strip())
        movie.append(country)
        movie.append(time)
        movie.append(published)
        movie.append(score)
        data.append(movie)
    return data


def save_data(data):
    sqlite = sqlite3.connect('网络爬虫数据库.db')
    cursor = sqlite.cursor()
    sql = '''create table 慢速网站爬虫
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
        sql = '''insert into 慢速网站爬虫
        values(%s)''' % ', '.join(item)
        cursor.execute(sql)
    sqlite.commit()
    sqlite.close()


def main():
    url = 'https://ssr4.scrape.center/'
    """电影数据网站，无反爬，每个响应增加了 5 秒延迟，适合测试慢速网站爬取或做爬取速度测试，减少网速干扰。"""
    start = time.time()
    html = get_html(url)
    data = get_data(html)
    save_data(data)
    print('运行时间：{:.6f}'.format(time.time() - start))


if __name__ == '__main__':
    main()
