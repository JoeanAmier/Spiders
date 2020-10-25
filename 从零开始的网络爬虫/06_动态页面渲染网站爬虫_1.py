from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ChromeOptions
import sqlite3
import time
from bs4 import BeautifulSoup
import re


def open_url(browser, url):
    browser.get(url)
    WebDriverWait(
        browser, timeout=5).until(
        lambda x: x.find_element_by_class_name('el-card__body'))
    html = browser.page_source
    return html


def get_data(url):
    findname = re.compile(
        r'<h2 class="m-b-sm" data-v-724ecf3b="">(.*?) - (.*?)</h2>')
    findtype = re.compile(
        r'<!-- --><!-- --><span>(.*?)\n')
    findinfo = re.compile(
        r'<span data-v-724ecf3b="">(.*?)</span><span data-v-724ecf3b=""> / </span><span data-v-724ecf3b="">(.*?)</span>'
        r'</div><div class="m-v-sm info" data-v-724ecf3b=""><span data-v-724ecf3b="">(.*?) 上映</span>')
    findscore = re.compile(
        r'<p class="score m-t-md m-b-n-sm" data-v-724ecf3b="">(.*?)</p>')
    template = url + 'page/'
    data = []
    option = ChromeOptions()
    option.add_argument('--headless')
    browser = webdriver.Chrome(options=option)
    for page in range(1, 11):
        base = template + str(page)
        html = open_url(browser, base)
        html = BeautifulSoup(html, 'html.parser')
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
            published = re.findall(findinfo, item)[0][2]
            score = re.findall(findscore, item)[0]
            movie.append(chinese_name)
            movie.append(english_name)
            movie.append(type)
            movie.append(country)
            movie.append(time)
            movie.append(published)
            movie.append(score)
            data.append(movie)
    browser.close()
    return data


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
    适合动态页面渲染爬取或 JavaScript 逆向分析
    此程序为动态页面渲染爬取"""
    start = time.time()
    data = get_data(url)
    save_data(data)
    print('运行时间：{:.6f}'.format(time.time() - start))


if __name__ == '__main__':
    main()
