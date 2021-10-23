import json
import os
import random
import re
import time

import requests
from bs4 import BeautifulSoup


def request_data(start):
    url = 'https://data.beijing.gov.cn/search/1_file/elevate'
    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.41'
                      '83.121 Safari/537.36'}
    data = {
        'q': '_text_:*',
        'wt': 'json',
        'rows': '10',
        'start': start,
        'enableElevation': 'true',
        'forceElevation': 'true',
        'sort': 'publishDate desc',
        'fl': '_uuid_,title,content,indexUrl,pubDateStr,pubDate,publishDate,publishDateStr,size,score,unitName,download'
              'Count,callCount,imgsrc,[elevated],imgsrc',
        'fq': '',
    }
    response = requests.post(url=url, headers=header, data=data)
    if response.status_code != 200:
        raise ValueError('请求项目列表失败')
    time.sleep(random.randrange(2, 5, 1))
    return response


def get_data(key):
    start = 0
    data = request_data(start)
    data = data.content.decode('utf-8')
    data = json.loads(data)
    content_id = data['response']['docs']
    content_id_list = []
    for item in content_id:
        indexUrl = item['indexUrl']
        indexUrl = re.findall(re.compile(r'/([0-9]*?).htm'), indexUrl)
        if bool(indexUrl):
            content_id_list.append(indexUrl[0])
        else:
            raise ValueError('提取数据失败')
        break
    get_api_id(content_id_list, key)
    pages = data['response']['numFound']
    for page in range(pages // 10):
        start = (page + 1) * 10
        data = request_data(start)
        data = data.content.decode('utf-8')
        data = json.loads(data)
        content_id = data['response']['docs']
        content_id_list = []
        for item in content_id:
            indexUrl = item['indexUrl']
            indexUrl = re.findall(re.compile(r'/([0-9]*?).htm'), indexUrl)
            if bool(indexUrl):
                content_id_list.append(indexUrl[0])
            else:
                raise ValueError('提取数据失败')
            break
        get_api_id(content_id_list, key)
        break


def get_download(id_list, key):
    api = 'http://data.beijing.gov.cn:80/cms/web/APIInterface/userApply.jsp?id={}&key={}'
    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.41'
                      '83.121 Safari/537.36'}
    for item in id_list:
        response = requests.get(api.format(item, key), headers=header)
        if response.status_code == 200:
            try:
                data = json.loads(response.text)
                url = data['result']['address']
                name = data['result']['name']
                save_data(name, url)
            except BaseException:
                raise ValueError(response.text)
        else:
            raise ValueError('请求api失败')


def save_data(name, url):
    root = os.getcwd() + '\\数据结果\\'
    path = root + name + '.' + url.split('.')[-1]
    if not os.path.exists(root):
        os.mkdir(root)
    if not os.path.exists(path):
        header = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.41'
                          '83.121 Safari/537.36'}
        response = requests.get(url, headers=header)
        time.sleep(random.randrange(2, 5, 1))
        with open(path, 'wb') as data:
            data.write(response.content)
            data.close()


def get_api_id(content_id, key):
    model = 'https://data.beijing.gov.cn/cms/web/APIInterface/dataDoc.jsp?contentID='
    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.41'
                      '83.121 Safari/537.36'}
    for item in content_id:
        response = requests.get(url=model + item, headers=header)
        time.sleep(random.randrange(2, 5, 1))
        if response.status_code != 200:
            raise ValueError('请求详情页失败')
        soup = BeautifulSoup(response.content.decode('utf-8'), 'lxml')
        id_list = [
            index.select('td:last-of-type')[0].text
            for index in soup.select(
                'div.content-box.fn-clear > table.content-tab:first-of-type > tbody > tr'
            )
        ]

        if bool(id_list):
            get_download(id_list, key)


def main():
    key = input('输入API唯一标识码（key）：')
    get_data(key)


if __name__ == '__main__':
    main()
