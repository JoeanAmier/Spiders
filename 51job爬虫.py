import requests
from urllib import parse
import json
import pymysql
import time
import random


def get_html(key, page=1):
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.418'
                      '3.121 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Host': 'search.51job.com',
        'Accept-Encoding': 'gzip, deflate, br',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Pragma': 'no-cache',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'https://search.51job.com/list/030000,000000,0000,00,9,99,{},2,{}.html?lang=c&postchannel=0000'
                   '&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&ord_field=0&dibiaoid=0&line=&w'
                   'elfare='.format(
                       parse.quote(key),
                       page)}
    url = 'https://search.51job.com/list/030000,000000,0000,00,9,99,{},2,{}.html?lang=c&postchannel=0000&workyear=99&' \
          'cotype=99&degreefrom=99&jobterm=99&companysize=99&ord_field=0&dibiaoid=0&line=&welfare='
    session = requests.Session()
    response = session.get(url.format(parse.quote(key), page), headers=header)
    if response.status_code == 200:
        return response.content.decode(response.encoding)
    else:
        raise Warning('请求网页失败')


def get_data(key, html, page):
    data, pages = deal_data(html)
    save_data(data)
    if page != 0:
        for i in range(2, page + 2):
            time.sleep(random.random() + random.randrange(2, 4, 1))
            html = get_html(key, page=i)
            data, pages = deal_data(html)
            save_data(data)
    print('获取数据结束')


def save_data(data):
    database = pymysql.connect('localhost', 'root', '数据库密码', '数据库名称')
    cursor = database.cursor()
    try:
        sql = '''create table 51job
            (链接 text,
            职位 text,
            发布日期 DATETIME,
            月薪 text,
            信息 text,
            福利 text,
            公司名称 text,
            公司性质 text,
            公司规模 text,
            行业分类 text)'''
        cursor.execute(sql)
        database.commit()
        print('新建表成功')
    except BaseException:
        pass
    sql = '''insert into 51job VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
    cursor.executemany(sql, data)
    database.commit()
    database.close()


def deal_data(data):
    data = json.loads(data)
    items = []
    engine_search_result = data['engine_search_result']
    for i in engine_search_result:
        cache = []
        job_href = i['job_href']
        job_name = i['job_name']
        issuedate = i['issuedate']
        if bool(i['providesalary_text']):
            providesalary_text = i['providesalary_text']
        else:
            providesalary_text = None
        if bool(i['attribute_text']):
            attribute_text = '%s' % ','.join(i['attribute_text'])
        else:
            attribute_text = None
        jobwelf_list = '%s' % ','.join(i['jobwelf_list'])
        if not bool(jobwelf_list):
            jobwelf_list = None
        company_name = i['company_name']
        companytype_text = i['companytype_text']
        if bool(i['companysize_text']):
            companysize_text = i['companysize_text']
        else:
            companysize_text = None
        companyind_text = i['companyind_text']
        cache.append(job_href)
        cache.append(job_name)
        cache.append(issuedate)
        cache.append(providesalary_text)
        cache.append(attribute_text)
        cache.append(jobwelf_list)
        cache.append(company_name)
        cache.append(companytype_text)
        cache.append(companysize_text)
        cache.append(companyind_text)
        items.append(cache)
    pages = data['jobid_count']
    return items, int(pages)


def get_page(html, page):
    item, items = deal_data(html)
    pages = items // 50 + 1 if items % 50 != 0 else items // 50
    if pages >= page >= 1:
        return page - 1
    print('获取到总页数为：' + str(pages) + '\n输入页数超出总页数或页数输入错误\n本次运行程序只获取第一页数据')
    return 0


def main():
    print('首次运行请在代码中修改MySQL数据库密码和数据库名称')
    key = input('请输入关键字：')
    page = int(input('请输入获取页数：'))
    html = get_html(key)
    page = get_page(html, page)
    get_data(key, html, page)


if __name__ == '__main__':
    main()
