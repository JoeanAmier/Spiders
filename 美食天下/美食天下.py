import requests
import time
import random
from bs4 import BeautifulSoup
import pymysql
import json
import os
import re

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
DATABASE = 'deliciousFood'

ROOT = os.getcwd() + '\\cache\\'


# if not os.path.exists(ROOT):
#     os.mkdir(ROOT)


def get_data():
    if os.path.exists('data.json'):
        with open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            data = data['data']
        return data
    else:
        with open('data.json', 'w', encoding='utf-8') as f:
            data = {
                "data": [[0, "url_1", "demo_1", 100],
                         [1, "url_2", "demo_2", 100]]
            }
            f.write(json.dumps(data))
        print('已在当前目录生成 data.json 文件')
        print('请在 data.json 文件输入程序必要信息后再运行本程序！')
        print(
            '格式: [索引（整数）, 链接（字符串）, 类型（字符串）, 爬取页数（整数）]\n按格式在 data.json 输入相关信息，注意最外侧还有一对中括号')
        print('爬取任务未完成时不要修改 data.json')
        return None


def check_data(data):
    if not data:
        return None
    _ = -1
    for i, j in enumerate(data):
        if j[0] - _ != 1:
            print(j, '索引错误')
            return None
        _ = i
        if not re.findall(
                r'^https://home.meishichina.com/recipe/[a-z0-9]*?/$',
                j[1]):
            print(j, '链接错误')
            return None
        if not j[2]:
            print(j, '类型错误')
            return None
        if j[3] < 1 or j[3] > 100:
            print(j, '爬取页数错误')
            return None
        data[i][1] = j[1] + 'page/{}/'
    return data


HEADERS_3 = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q'
              '=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'no-cache',
    'dnt': '1',
    'pragma': 'no-cache',
    'referer': 'https://home.meishichina.com/',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chro'
                  'me/87.0.4280.141 Safari/537.36'}


def get_json():
    if os.path.exists('MySQL.json'):
        with open('MySQL.json', 'r') as f:
            template = json.load(f)
            host = template['host']
            user = template['user']
            password = template['password']
        return host, user, password
    else:
        with open('MySQL.json', 'w') as f:
            template = {'host': '', 'user': '', 'password': ''}
            f.write(json.dumps(template))
        print('已在当前目录生成 MySQL.json 文件')
        print('请在 MySQL.json 文件输入数据库信息后再运行本程序！')
        return None, None, None


def create_db(host, user, password):
    try:
        db = pymysql.connect(host=host, user=user, password=password)
    except pymysql.err.OperationalError:
        print('连接数据库失败，请检查 MySQL.json 文件')
        exit()
    sql = f"create database {DATABASE} CHARACTER SET utf8mb4"
    cursor = db.cursor()
    try:
        cursor.execute(sql)
    except pymysql.err.ProgrammingError:
        pass
    db.commit()
    db.close()


def create_table(db, cursor):
    # sql = """create table {}(
    # ID MEDIUMINT primary key,
    # 链接 text not null,
    # 菜名 text not null,
    # 食材 text not null,
    # 步骤 text not null,
    # 效果图 text not null)"""
    # # 图片数据 MEDIUMBLOB
    # for i in list_:
    #     try:
    #         cursor.execute(sql.format(i[2]))
    #         db.commit()
    #     except pymysql.err.OperationalError:
    #         continue
    sql = """create table if not exists 美食天下(
        ID MEDIUMINT primary key,
        链接 text not null,
        菜名 text not null,
        食材 text not null,
        步骤 text not null,
        效果图 text not null,
        类型 text not null)"""
    # 图片数据 MEDIUMBLOB
    cursor.execute(sql)
    db.commit()


def wait_time():
    time.sleep(random.random() + random.randint(1, 5))


def get_urls(session, url, page):
    global HEADERS_1
    url = url.format(page)
    print('当前网址：', url)
    response = session.get(url, headers=HEADERS_1)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'lxml')
        urls = [i['href']
                for i in soup.select('ul > li > div.detail > h2 > a')]
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


def get_img(url):
    global HEADERS_3
    response = requests.get(url, headers=HEADERS_3)
    if response.status_code == 200:
        wait_time()
        return response.content
    else:
        print(response.status_code, url)
        return None


def save_img(id_, img):
    if img:
        global ROOT
        root = os.path.join(ROOT, id_ + '.jpg')
        with open(root, 'wb') as f:
            f.write(img)
        print(f'已保存图片：{id_}')
    else:
        print(f'保存图片失败：{id_}')


def image_data(id_):
    global ROOT
    root = os.path.join(ROOT, id_ + '.jpg')
    with open(root, 'rb') as f:
        img = f.read()
    return img


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
    """需要下载图片到本地请取消注释"""
    # save_img(id_, get_img(img))
    data = [
        id_,
        link,
        title,
        '%s' %
        ','.join(ingredients),
        '%s' %
        ''.join(step).replace('"', "'"),
        img]
    if None not in data:
        return data
    print(data)
    return None


def get_id(url):
    return re.findall(
        r'^https://home.meishichina.com/recipe-([0-9]*?).html',
        url)[0]


def save_data(db, cursor, data, type_):
    save = True
    data.append(type_)
    for i in range(7):
        data[i] = '"' + data[i] + '"'
    sql = """insert into 美食天下 (ID, 链接, 菜名, 食材, 步骤, 效果图, 类型)
    values(%s)""" % ','.join(data)
    try:
        cursor.execute(sql)
        db.commit()
        print('已保存数据', data[0], data[2])
    except pymysql.err.IntegrityError:
        save = False
    # try:
    #     if data[-1] and save:
    #         sql = "insert into %s (图片数据) values (%s)"
    #         args = (type_, pymysql.Binary(data[-1]))
    #         cursor.execute(sql, args)
    #         db.commit()
    #         print('已保存图片', data[0], data[2])
    # except pymysql.err.IntegrityError:
    #     save = False
    return save


def save_process(progress):
    with open('progress.json', 'w') as f:
        f.write(json.dumps(progress))


def main():
    print('除非发生未知异常，否则不要直接关闭程序')
    print('爬取任务未完成时不要修改 data.json')
    _ = get_data()
    crawler_data = check_data(_)
    host, user, password = get_json()
    if None in [crawler_data, host, user, password]:
        print('data.json 或 MySQL.json 文件内容错误')
        exit()
    create_db(host, user, password)
    db = pymysql.connect(
        host=host,
        user=user,
        password=password,
        db=DATABASE)
    cursor = db.cursor()
    create_table(db, cursor)
    over = False
    if os.path.exists('progress.json'):
        with open('progress.json', 'r') as f:
            progress = json.load(f)
        if progress['type'] == len(
                crawler_data) - 1 and progress['page'] > crawler_data[progress['type']][3]:
            print('已获取全部数据，现在可以修改 data.json 文件')
            over = True
            progress['type'] += 1
            progress['page'] = 1
        elif progress['type'] == len(crawler_data):
            print('已获取全部数据，现在可以修改 data.json 文件')
            over = True
    else:
        progress = {'type': 0, 'page': 1}
    _ = progress.copy()
    start_type = _['type']
    start_page = _['page']
    session = requests.Session()
    for item in crawler_data[start_type:]:
        if over:
            break
        progress['type'] = item[0]
        if progress['page'] > item[3]:
            progress['page'] = 1
            break  # 单次运行只爬取一种类型
        for page in range(start_page, item[3] + 1):
            # if page - start_page >= 10:
            #     """单次运行爬取10页，注释代码块可取消限制，修改代码可修改单次爬取页数"""
            #     over = True
            time.sleep(random.random() + random.randint(5, 15))
            if over:
                break
            print('正在爬取 {} 的第 {} 页数据'.format(item[2], page))
            session, urls = get_urls(session, item[1], page)
            if session and urls:
                for info in urls:
                    # break  # 测试使用
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
                    break  # 测试使用
                progress['page'] = page if over else page + 1
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
