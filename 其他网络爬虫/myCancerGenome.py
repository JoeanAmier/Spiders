import os
import pickle
import random
import time

import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient


def get_data(hits):
    path = os.getcwd() + '\\data'
    all = hits // 10 + 2 if hits % 10 else hits // 10 + 1
    if os.path.exists(path):
        with open('data', 'rb') as f:
            data = pickle.load(f)
            long = len(data)
            print('当前列表数据数量：', long)
            if long == hits:
                print('列表数据获取完毕')
                return
            long = long // 10 + 1
            all_data = data
    else:
        all_data = []
        long = 1
    session = requests.Session()
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/8'
                      '7.0.4280.67 Safari/537.36 Edg/87.0.664.47',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,applica'
                  'tion/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'cache-control': 'no-cache',
        'dnt': '1',
        'pragma': 'no-cache',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1'}
    try:
        session.get(
            'https://www.mycancergenome.org/content/biomarkers/',
            headers=headers,
            timeout=10)
    except BaseException:
        raise TimeoutError('获取会话超时')
    url = 'https://www.mycancergenome.org/mcg/omni_mcg/biomarkers/?fields=alteration_groups&fields=name&fields=biomarke' \
          'r_type&fields=genes&fields=in_diseases&fields=pathways&fields=summary&fields=trial_count&fields=therapy_coun' \
          't&fields=drug_count&page={}&search='
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/8'
                      '7.0.4280.67 Safari/537.36 Edg/87.0.664.47',
        'authorization': 'Token 989c38a36eec154f01167274dbce2334ccf8ef11',
        'accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'cache-control': 'no-cache',
        'dnt': '1',
        'pragma': 'no-cache',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'referer': 'https://www.mycancergenome.org/content/biomarkers/'}
    z = 0
    for page in range(long, all):
        try:
            response = session.get(
                url.format(page), headers=headers, timeout=10)
            z += 1
        except BaseException:
            print('获取列表超时')
            break
        time.sleep(random.randrange(1, 4, 1) + random.random())
        if response.status_code == 200:
            cache = response.json()
            for i in range(len(cache['results'])):
                data = []
                data.append(cache['results'][i]['name'])
                try:
                    data.append(cache['results'][i]['drug_count'])
                except BaseException:
                    pass
                all_data.append(data)
        else:
            print('发生异常，响应码：', response.status_code)
            break
        """
        启用此代码则每次运行只获取10条数据
        注释此代码则运行获取全部数据
        """
        # break  # 调试使用
        """
        启用此代码则每次运行获取1000条数据
        注释此代码则运行获取全部数据
        """
        if z >= 100:
            print(len(all_data))
            break
    with open('data', 'wb') as f:
        pickle.dump(all_data, f)


def get_info():
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q'
                  '=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'no-cache',
        'dnt': '1',
        'pragma': 'no-cache',
        'referer': 'https://www.mycancergenome.org/content/biomarkers/',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/8'
                      '7.0.4280.66 Safari/537.36'}
    path = os.getcwd() + '\\progress'
    if os.path.exists(path):
        with open('progress', 'rb') as f:
            progress = pickle.load(f)
            print('当前数据数量：', progress)
    else:
        progress = 0
    with open('data', 'rb') as f:
        data = pickle.load(f)
    client = MongoClient()
    db = client['癌症基因组数据库']
    collection = db['详细数据']
    z = 0
    for i in data[progress:]:
        """
        部分基因无法访问详情页
        """
        if i[0] in ['MALT1']:
            continue
        if len(i) == 1:
            info = {'Drugs': None, 'Info': None, 'Name': i[0]}
            save_data(info, collection)
            progress += 1
        elif len(i) == 2 and i[1] == 0:
            info = {'Info': None, 'Name': i[0], 'Drugs': i[1]}
            save_data(info, collection)
            progress += 1
        elif len(i) == 2:
            try:
                z += 1
                cache = open_url_T_1(headers, i[0])
                if cache:
                    info = {'Name': i[0], 'Drugs': i[1], 'Info': cache}
                    save_data(info, collection)
                    time.sleep(random.randrange(1, 4, 1) + random.random())
                else:
                    print('访问超时或响应码错误，请重试')
                    break
            except BaseException:
                time.sleep(random.randrange(1, 4, 1) + random.random())
                z += 1
                try:
                    cache = open_url_T_2(headers, i[0])
                except ValueError:
                    break
                if cache == 'None':
                    info = {'Name': '', 'Drugs': '', 'Info': None}
                    info['Name'] = i[0]
                    info['Drugs'] = i[1]
                    save_data(info, collection)
                else:
                    if cache:
                        info = {'Name': '', 'Drugs': '', 'Info': ''}
                        info['Name'] = i[0]
                        info['Drugs'] = i[1]
                        info['Info'] = cache
                        save_data(info, collection)
                    else:
                        print('访问超时或响应码错误，请重试')
                        break
            progress += 1
        else:
            raise ValueError(i)
        # break  # 调试使用
        """
        启用此代码则每次运行发送50次请求后关闭程序
        注释此代码则运行获取全部数据
        """
        if z >= 500:
            break
    with open('progress', 'wb') as f:
        pickle.dump(progress, f)
        print('已获取数据数量：', progress)  # 调试使用


def auto_name(name):
    name = name.replace(')',
                        '').replace('*',
                                    '').replace('_',
                                                '-').replace('(',
                                                             '-').replace(';',
                                                                          '-').replace(' ',
                                                                                       '-').replace('--',
                                                                                                    '-').lower()
    return name


def open_url_F(name):
    """
    暂时不需要调用
    """
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q='
                  '0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'no-cache',
        'dnt': '1',
        'pragma': 'no-cache',
        'referer': 'https://www.mycancergenome.org/content/biomarkers/',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/8'
                      '7.0.4280.66 Safari/537.36'}
    url = 'https://www.mycancergenome.org/content/alteration/{}/'
    response = requests.get(url.format(name), headers=headers)
    html = response.content.decode(response.encoding)
    soup = BeautifulSoup(html, 'lxml')
    num = soup.select(
        'body > div.main-content > div.alteration-detail > div.row.header > div.small-12.medium-9.column'
        's > div:nth-child(1) > div > p > a')[0].text
    print(soup.select('body > div.main-content > div.alteration-detail > div.row.header > div.small-12.medium-9.column'
                      's > div:nth-child(2) > div > p:nth-child({})'.format(int(num) + 1))[0].text.strip())


def open_url_T_1(
        headers,
        name,
        url='https://www.mycancergenome.org/content/alteration/{}/'):
    try:
        response = requests.get(
            url.format(
                auto_name(name)),
            headers=headers,
            timeout=10)
        # print(response.url)  # 调试代码
        # print(response.status_code)
    except BaseException:
        return None
    if response.status_code == 200:
        data = [name, response.url]
        html = response.content.decode(response.encoding)
        soup = BeautifulSoup(html, 'lxml')
        info = soup.select('div#therapies-toggle > p')
        content = ''.join(i.text for i in info)
        data.append(content.replace('\n', '').replace('  ', '').strip())
        num = soup.select('div#therapies-toggle > p:last-of-type > a')[0].text
        reference = soup.select(
            'div.small-12.columns > p.reference')[int(num) - 1].text
        data.append(reference.replace('\n', '').replace('  ', '').strip())
        BDT = soup.select(
            'div#therapies-toggle > div.about-alteration-therapy-row')
        data.append({})
        for a in BDT:
            title = a.select(
                'p.about-alteration-therapy-header')[0].text.replace('+', '').strip()
            if title not in ['Bosutinib', 'Imatinib']:
                continue
            data[4][title] = []
            Bosutinib = a.select(
                'div.about-alteration-therapy-content > div.about-alteration-therapy-disease-row')
            for b, c in enumerate(Bosutinib):
                data[4][title].append([])
                t1 = c.select(
                    'p.about-alteration-therapy-disease-header')[0].text.replace('-', '')
                data[4][title][b].append(
                    t1.replace(
                        '\n', '').replace(
                        '  ', '').strip())
                t2 = c.select(
                    'div.row.table-row.targeted-therapy-table-small-screen-container')
                for f in t2:
                    data[4][title][b].append([])
                    t3 = f.select('div.small-12.columns.biomarker-criteria')
                    data[4][title][b][-1].append(t3[0].text.replace(
                        '\n', '').replace('  ', '').strip())
                    row = f.select(
                        'div.small-12.columns.response-setting-note > div.row')
                    data[4][title][b][-1].append([])
                    for d, e in enumerate(row):
                        data[4][title][b][-1][-1].append(
                            e.text.replace('\n', '').replace('  ', '').strip())
        return data
    elif response.status_code == 404:
        raise ValueError
    else:
        print(response.url)
        return None


def open_url_T_2(
        headers,
        name,
        url='https://www.mycancergenome.org/content/gene/{}/'):
    try:
        response = requests.get(
            url.format(
                auto_name(name)),
            headers=headers,
            timeout=10)
        # print(response.url)  # 调试代码
        # print(response.status_code)
    except BaseException:
        return None
    if response.status_code == 200:
        data = [name, response.url]
        html = response.content.decode(response.encoding)
        soup = BeautifulSoup(html, 'lxml')
        info = soup.select('div#therapies-toggle > p')
        content = ''.join(i.text for i in info)
        data.append(content.replace('\n', '').replace('  ', '').strip())
        try:
            num = soup.select(
                'div#therapies-toggle > p:last-of-type > a')[0].text
        except IndexError:
            return 'None'
        reference = soup.select(
            'div.small-12.columns > p.reference')[int(num) - 1].text
        data.append(reference.replace('\n', '').replace('  ', '').strip())
        BDT = soup.select('div#therapies-toggle > div.about-gene-therapy-row')
        data.append({})
        for a in BDT:
            title = a.select(
                'p.about-gene-therapy-header')[0].text.replace('+', '').strip()
            if title not in ['Bosutinib', 'Imatinib']:
                continue
            data[4][title] = []
            Bosutinib = a.select(
                'div.about-gene-therapy-content > div.about-gene-therapy-disease-row')
            for b, c in enumerate(Bosutinib):
                data[4][title].append([])
                t1 = c.select(
                    'p.about-gene-therapy-disease-header')[0].text.replace('-', '')
                data[4][title][b].append(
                    t1.replace(
                        '\n', '').replace(
                        '  ', '').strip())
                t2 = c.select(
                    'div.row.table-row.targeted-therapy-table-small-screen-container')
                for f in t2:
                    data[4][title][b].append([])
                    t3 = f.select('div.small-12.columns.biomarker-criteria')
                    data[4][title][b][-1].append(t3[0].text.replace(
                        '\n', '').replace('  ', '').strip())
                    row = f.select(
                        'div.small-12.columns.response-setting-note > div.row')
                    data[4][title][b][-1].append([])
                    for d, e in enumerate(row):
                        data[4][title][b][-1][-1].append(
                            e.text.replace('\n', '').replace('  ', '').strip())
        return data
    elif response.status_code == 302:
        print(name, response.url)
        raise ValueError
    else:
        print(response.url)
        return None


def save_data(data, collection):
    collection.insert_one(data)


def main():
    hits = 16380  # 数据总数，手动修改
    get_data(hits)
    get_info()
    print('程序已结束')


if __name__ == '__main__':
    main()
