from requests_html import HTMLSession
from fake_useragent import FakeUserAgent
import re
import json
import sqlite3


def get_link(session, headers):
    url = 'https://dxy.com/diseases'
    response = session.get(url, headers=headers)
    link = [
        i.attrs['href']
        for i in response.html.find('div.section-filter-box-wrap.normal > a')
    ]
    return session, link


def get_disease_link(session, link, headers):
    json_re = re.compile(r'window.\$\$data=(.*)')
    disease = []
    tag_name = []
    for i in link:
        response = session.get(i, headers=headers)
        script = response.html.find('script')
        if not script[3]:
            print('匹配 script 失败！')
            break
        json_ = re.findall(json_re, script[3].text)
        if not json_:
            print('JSON 格式化失败！')
            break
        data = json.loads(json_[0])
        for j in data['diseases'][1:]:
            for x in j['tag_list']:
                tag_id = x['tag_id']
                tag_name.append(x['tag_name'])
                disease.append(tag_id)
        break  # 调试代码
    return session, disease, tag_name


def get_tag(session, disease, headers):
    url = 'https://dxy.com/disease/{}/detail'
    data = []
    for i in disease:
        response = session.get(url.format(i), headers=headers)
        data.append([j.text for j in response.html.find(
            'div.tag-content-tags > a')])
        break  # 调试代码
    return data


# def save_data(tag_name, data):
#     db = sqlite3.connect('疾病标签数据库.db')
#     cursor = db.cursor()
#     sql = """create table 疾病标签
#     (疾病名称
#     标签)"""


def main():
    session = HTMLSession()
    headers = {
        'user-agent': FakeUserAgent().chrome,
        'referer': 'https://dxy.com/',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,applic'
                  'ation/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'upgrade-insecure-requests': '1'}
    session, link = get_link(session, headers)
    session, disease, tag_name = get_disease_link(session, link, headers)
    data = get_tag(session, disease, headers)
    if len(tag_name) <= len(data):
        print('爬取发生异常！')
        exit()
    print(data)


if __name__ == '__main__':
    main()
