from bs4 import BeautifulSoup
import xlwt
import re
import urllib.request
import sqlite3
import time
import pymysql


def main(means):  # 以不同的格式进行保存数据
    if means == '表格':  # 以xlsx格式保存
        douban = 'https://movie.douban.com/top250?start='
        datalist = get_data(douban)
        try:
            savexlsx(datalist)
            print('爬取成功，文件已保存')
        except PermissionError:
            print('文件已打开，无法写入数据')
            print('请重新运行')
    elif means == 'SQLite':  # 以sqlite格式保存数据
        douban = 'https://movie.douban.com/top250?start='
        datalist = get_data(douban)
        dbpath = '数据库.db'
        savedb(datalist, dbpath)
    elif means == 'MySQL':
        douban = 'https://movie.douban.com/top250?start='
        datalist = get_data(douban)
        mysql_save(datalist)
    else:
        print('保存格式错误')


# 正则表达式规则
findlink = re.compile(r'<a href="(.*?)"')
findtitle = re.compile(r'<span class="title">(.*?)</span>')
findscore = re.compile(r'<span class=".*?" property=".*?">(.*?)</span>')
findpeople = re.compile(r'<span>(.*)人评价</span>')
findinfo = re.compile(r'<span class="inq">(.*?)</span>')
findtype = re.compile(r'''导演.*?<br/>
                            .* / .* / (.*)''')


# 解析网址
def askURL(douban):
    # 设置浏览器UA
    User = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.41"
                      "47.89 Safari/537.36 Edg/84.0.522.40Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.3"
                      "6 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36 Edg/84.0.522.40"}
    # 携带参数访问网址
    request = urllib.request.Request(url=douban, headers=User)  # 指定参数
    response = urllib.request.urlopen(request)  # 解析网址
    html = response.read().decode('utf-8')  # 记录源码
    return html  # 返回数据


# 翻页爬取
def get_data(douban):
    data_list = []  # 总数据，包含全部电影信息
    for i in range(0, 10):  # 每一页获取网页源码
        print('正在解析第' + str(i) + '页')
        url = douban + str(i * 25)
        html = askURL(url)  # 返回一页网页源码
        time.sleep(2)
        print('获取成功')
        soup = BeautifulSoup(html, 'html.parser')  # 解析网页源码
        for item in soup.find_all('div', class_="item"):  # 解析每一部电影信息
            data = []  # 临时储存数据，包含一部电影信息
            item = str(item)  # 转化为字符串
            link = re.findall(findlink, item)[0]  # link为字符串元素
            data.append(link)  # 添加临时储存数据
            title = re.findall(findtitle, item)
            if len(title) == 2:
                c = title[0].replace('/', '')  # 替换字符串内容，查找元素，替换为
                data.append(c)
                e = title[1].replace('/', '')
                e = e.strip()
                data.append(e)
            else:
                data.append(title[0])
                data.append('无')
            score = re.findall(findscore, item)[0]
            score = score.strip()
            data.append(score)
            people = re.findall(findpeople, item)[0]
            people = people.strip()
            data.append(people)
            info = re.findall(findinfo, item)
            if len(info) == 0:
                data.append('无')
            else:
                data.append(info[0])
            type = re.findall(findtype, item)[0]
            type = type.strip()
            data.append(type)
            data_list.append(data)  # 把一部电影的信息以列表形式添加到总数据
    return data_list  # 返回全部电影信息


def savexlsx(datalist):
    book = xlwt.Workbook(encoding='utf-8')
    sheet = book.add_sheet('爬取结果', cell_overwrite_ok=True)  # 覆盖写入
    tap = ('链接', '电影名称', '英文名称', '评分', '评价人数', '介绍', '类型')
    for i in range(0, 7):
        sheet.write(0, i, tap[i])  # 添加列标签
    for i in range(0, 250):
        tap = datalist[i]
        print('正在保存第' + str(i + 1) + '条')
        for j in range(0, 7):
            data_1 = tap[j]
            sheet.write(i + 1, j, data_1)
    book.save('豆瓣TOP250.xlsx')


def savedb(datalist, dbpath):
    list = sqlite3.connect(dbpath)
    cursor = list.cursor()
    basesql = '''create table 豆瓣top250
    ('TOP' integer primary key not null ,
    '链接' text not null,
    '电影名称' text  not null,
    '英文名称' text,
    '评分' number not null,
    '评价人数' number not null,
    '介绍' text,
    '类型' text not null)'''
    try:
        cursor.execute(basesql)
        list.commit()
    except sqlite3.OperationalError:
        print('数据表已存在')
    for i, data in enumerate(datalist):  # 把索引赋给i，把元素赋给data
        for index in range(0, 7):
            data[index] = '"' + str(data[index]) + '"'
        sql = '''insert into 豆瓣top250('链接', '电影名称',
            '英文名称', '评分', '评价人数', '介绍', '类型')
            values(%s)''' % ','.join(data)
        # print(sql)
        # break
        # %占位符，以逗号为分隔符，把data连接起来
        cursor.execute(sql)
        print('正在保存第' + str(i + 1) + '条数据')
        list.commit()
    print('数据表已保存完毕')
    list.close()
    print('数据库已关闭')


def mysql_save(datalist):
    database = pymysql.connect('localhost', 'root', '202230', 'YongQuan')
    try:
        sql = '''create table 豆瓣top250
            (TOP int(3) primary key auto_increment,
            链接 text,
            电影名称 text,
            英文名称 text,
            评分 float,
            评价人数 mediumint,
            介绍 text,
            类型 text)'''
        cursor = database.cursor()
        cursor.execute(sql)
        database.commit()
        print('新建表成功')
    except:
        print('数据表已存在')
    for i, data in enumerate(datalist):  # 把索引赋给i，把元素赋给data
        for index in range(0, 7):
            data[index] = '"' + str(data[index]) + '"'
        sql = '''insert into 豆瓣top250(链接, 电影名称,
            英文名称, 评分, 评价人数, 介绍, 类型)
            values(%s)''' % ','.join(data)
        cursor.execute(sql)
        print('正在保存第' + str(i + 1) + '条数据')
        database.commit()
    print('数据表已保存完毕')
    database.close()
    print('数据库已关闭')


if __name__ == '__main__':
    print('使用MySQL数据库保存爬取数据需要先安装MySQl')
    means = str(input('输入保存形式：xlsx表格、SQLite数据库、MySQL数据库'))
    start = time.time()
    main(means)
    print('运行时间：%.5f' % float(time.time() - start))
    print('程序已关闭')
