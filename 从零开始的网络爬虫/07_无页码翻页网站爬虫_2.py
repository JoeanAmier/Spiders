import sqlite3
import time
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.keys import Keys


def get_html(url):
    try:
        option = ChromeOptions()
        option.add_argument('--headless')
        browser = webdriver.Chrome(options=option)
        browser.get(url)
        time.sleep(10)
        webdriver.ActionChains(browser).key_down(Keys.END)
        time.sleep(2)
        webdriver.ActionChains(browser).key_up(Keys.END)
        time.sleep(2)
        html = browser.page_source
        return html
    except BaseException:
        raise ValueError('发生错误')
    finally:
        browser.quit()


def get_data(html):
    html = BeautifulSoup(html, 'html.parser')
    data = []
    for item in html.findAll('div', class_='el-card__body'):
        try:
            movie = []
            name = item.select(
                'a.router-link-exact-active.router-link-active > h2')[0].text
            chinese_name = name.split(' - ')[0]
            english_name = name.split(' - ')[1]
            type = [i.text.strip()
                    for i in item.select('div.categories > button > span')]
            country = item.select(
                'div.el-col-md-16 > div.m-v-sm.info:nth-child(3) > span')[0].text
            time = item.select(
                'div.el-col-md-16 > div.m-v-sm.info:nth-child(3) > span')[2].text
            published = item.select(
                'div.el-col-md-16 > div.m-v-sm.info:nth-child(4) > span')[0]
            if len(published) == 1:
                published = published.text
            else:
                published = None
            score = item.select('p.score.m-t-md.m-b-n-sm')[0].text
            movie.append(chinese_name)
            movie.append(english_name)
            movie.append('%s' % ','.join(type))
            movie.append(country.strip())
            movie.append(time.strip())
            movie.append(published.strip())
            movie.append(score.strip())
            data.append(movie)
        except IndexError:
            continue
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
    url = 'https://spa3.scrape.center/'
    """
    电影数据网站，无反爬，数据通过 Ajax 加载，无页码翻页，下拉至底部刷新，适合 Ajax 分析和动态页面渲染爬取。
    本程序使用动态网站渲染方法爬取
    代码测试时间：2020/12/10
    """
    start = time.time()
    html = get_html(url)
    data = get_data(html)
    save_data(data)
    print('运行时间：{:.6f}'.format(time.time() - start))


if __name__ == '__main__':
    main()
