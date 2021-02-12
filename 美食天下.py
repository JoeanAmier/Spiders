import requests
import time
import random
from bs4 import BeautifulSoup
import pymysql
import json
import os
import re

LINK = [[0, 'https://home.meishichina.com/recipe/recai/page/{}/', '热菜'],
        [1, 'https://home.meishichina.com/recipe/liangcai/page/{}/', '凉菜'],
        [2, 'https://home.meishichina.com/recipe/tanggeng/page/{}/', '汤羹'],
        [3, 'https://home.meishichina.com/recipe/zhushi/page/{}/', '主食'],
        [4, 'https://home.meishichina.com/recipe/xiaochi/page/{}/', '小吃'],
        [5, 'https://home.meishichina.com/recipe/xican/page/{}/', '西餐']]
HEADERS_1 = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,applicatio'
              'n/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'DNT': '1',
    'Host': 'home.meishichina.com',
    'Pragma': 'no-cache',
    'Referer': 'https://www.meishichina.com/',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-site',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/8'
                  '8.0.4324.150 Safari/537.36 Edg/88.0.705.63'}

HEADERS_2 = HEADERS_1.copy()
del HEADERS_2['Referer']
DATABASE = 'meishichina'


def get_json():
    if os.path.exists('MySQL.json'):
        with open('MySQL.json', 'r') as f:
            template = json.load(f)
            user = template['user']
            password = template['password']
        return user, password
    else:
        with open('MySQL.json', 'w') as f:
            template = {'user': '', 'password': ''}
            f.write(json.dumps(template))
        print('已在当前目录生成 MySQL.json 文件')
        print('请在 MySQL.json 文件保存数据库信息后再运行本程序！')
        exit()


def create_db(user, password):
    try:
        db = pymysql.connect(host='localhost', user=user, password=password)
    except pymysql.err.OperationalError:
        print('连接数据库失败，请检查 MySQL.json 文件')
        exit()
    sql = f"create database {DATABASE}"
    cursor = db.cursor()
    try:
        cursor.execute(sql)
    except pymysql.err.ProgrammingError:
        pass
    db.commit()
    db.close()


def create_table(db, cursor):
    global LINK
    sql = """create table {}(
    ID MEDIUMINT primary key,
    链接 text not null,
    菜名 text not null,
    食材 text not null,
    步骤 text not null,
    效果图 text not null)"""
    for i in LINK:
        try:
            cursor.execute(sql.format(i[2]))
            db.commit()
        except pymysql.err.OperationalError:
            return


def wait_time():
    time.sleep(random.random() + random.randint(1, 5))


def get_urls(session, url, page):
    global HEADERS_1
    url = url.format(page)
    print('当前网址：', url)
    response = session.get(url, headers=HEADERS_1)
    if response.status_code == 200:
        urls = []
        soup = BeautifulSoup(response.content, 'lxml')
        for i in soup.select('ul > li > div.detail > h2 > a'):
            urls.append(i['href'])
        wait_time()
        return session, urls
    else:
        print(url, response.status_code)
        return None, None


def open_url(session, url):
    global HEADERS_2
    response = session.get(url, headers=HEADERS_2)
    if response.status_code == 200:
        wait_time()
        return session, response.content
    else:
        print(url, response.status_code)
        return None, None


def deal_data(html):
    soup = BeautifulSoup(html, 'lxml')
    try:
        link = soup.select('h1.recipe_De_title > a')[0]['href']
        title = soup.select('h1.recipe_De_title > a')[0]['title']
        img = soup.select('div.recipe_De_imgBox > a')[0].img['src']
        ingredients = [i.text for i in soup.select('fieldset.particulars b')]
        step = [i.text for i in soup.select(
            'div.recipeStep > ul > li > div.recipeStep_word')]
    except IndexError:
        return 'Error'
    id_ = get_id(link)
    data = [
        id_,
        link,
        title,
        '%s' %
        ','.join(ingredients),
        '%s' %
        ''.join(step).replace('"', "'"),
        img]
    if None in data:
        print(data)
        return None
    else:
        return data


def get_id(url):
    id_ = re.findall(
        r'https://home.meishichina.com/recipe-([0-9]*?).html',
        url)[0]
    return id_


def save_data(db, cursor, data, type):
    for i in range(6):
        data[i] = '"' + data[i] + '"'
    sql = """insert into {}
    values({})""".format(type, '%s' % ','.join(data))
    try:
        cursor.execute(sql)
        db.commit()
        print('已保存数据', data[0], data[2])
        return True
    except pymysql.err.IntegrityError as e:
        print(data)
        print(type)
        print(e)
        ok = 'Y'
        # ok = input('疑似发生异常（可能是数据重复），是否继续运行？\n（输入 Y 继续运行，不要直接停止程序！！！）')
        if ok == 'Y':
            return True
        else:
            return False


def save_process(progress):
    with open('progress.json', 'w') as f:
        f.write(json.dumps(progress))


def main():
    user, password = get_json()
    create_db(user, password)
    db = pymysql.connect(
        host='localhost',
        user=user,
        password=password,
        db=DATABASE)
    cursor = db.cursor()
    create_table(db, cursor)
    if os.path.exists('progress.json'):
        with open('progress.json', 'r') as f:
            progress = json.load(f)
        if progress['type'] == 5 and progress['page'] > 100:
            print('已获取全部数据')
            exit()
    else:
        progress = {'type': 0, 'page': 1}
    _ = progress.copy()
    start_type = _['type']
    start_page = _['page']
    session = requests.Session()
    over = False
    # over = True
    print('除非发生未知异常，否则不要直接关闭程序')
    for item in LINK[start_type:]:
        if over:
            break
        progress['type'] = item[0]
        if progress['page'] > 100:
            progress['page'] = 1
            break
        for page in range(start_page, 101):
            # if (n := (page - start_page)) >= 10:
            #     """单次运行爬取10页，注释代码块可取消限制"""
            #     print(f'本次运行已爬取 {n} 页数据')
            #     over = True
            # time.sleep(random.random() + random.randint(10, 30))
            if over:
                break
            print('正在爬取{}的第{}页数据'.format(item[2], page))
            session, urls = get_urls(session, item[1], page)
            if session and urls:
                for info in urls:
                    if over:
                        break
                    session, html = open_url(session, info)
                    if session and html:
                        data = deal_data(html)
                        if data == 'Error':
                            print('疑似无效链接：', info)
                            continue
                        elif data:
                            result = save_data(db, cursor, data, item[2])
                            if not result:
                                over = True
                                break
                        else:
                            over = True
                            break
                    else:
                        over = True
                        break
                if over:
                    progress['page'] = page
                else:
                    progress['page'] = page + 1
            else:
                over = True
                break
    save_process(progress)
    db.close()
    print('程序已退出')


if __name__ == '__main__':
    start_time = time.time()
    main()
    print('本次运行时间：{:.6f}'.format(time.time() - start_time))
