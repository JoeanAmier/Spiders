import requests
from bs4 import BeautifulSoup
import pickle
import os
import time
import random
import pymongo


def get_data(hits):
    path = os.getcwd() + '\\data'
    if hits % 10:
        all = hits // 10 + 1
    else:
        all = hits // 10
    if os.path.exists(path):
        with open('data', 'rb') as f:
            data = pickle.load(f)
            long = len(data)
            if long == hits:
                return
            long = long // 10 + 1
            all_data = data
    else:
        all_data = []
        long = 1
    session = requests.Session()
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/8'
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
    session.get('https://www.mycancergenome.org/content/biomarkers/', headers=headers)
    url = 'https://www.mycancergenome.org/mcg/omni_mcg/biomarkers/?fields=alteration_groups&fields=name&fields=biomarke' \
          'r_type&fields=genes&fields=in_diseases&fields=pathways&fields=summary&fields=trial_count&fields=therapy_coun' \
          't&fields=drug_count&page={}&search='
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/8'
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
    for page in range(long, all):
        response = session.get(url.format(page), headers=headers)
        time.sleep(random.randrange(1, 4, 1) + random.random())
        if response.status_code == 200:
            cache = response.json()
            for i in range(len(cache['results'])):
                data = []
                data.append(cache['results'][i]['name'])
                try:
                    data.append(cache['results'][i]['drug_count'])
                except:
                    pass
                all_data.append(data)
            break
        else:
            print('IP被封了')
            break
    with open('data', 'wb') as f:
        pickle.dump(all_data, f)


def get_info():
    path = os.getcwd() + '\\progress'
    if os.path.exists(path):
        with open('progress', 'rb') as f:
            progress = pickle.load(f)
    else:
        progress = 0
    with open('data', 'rb') as f:
        data = pickle.load(f)
    for i in data[progress:]:
        if len(i) == 1:
            progress += 1
        elif len(i) == 2 and i[1] == 0:
            progress += 1
        elif len(i) == 2:
            i = i[0].replace(' ', '-').lower()
            progress += 1
        else:
            raise ValueError
        time.sleep(random.randrange(1, 4, 1) + random.random())
    with open('progress', 'wb') as f:
        pickle.dump(progress, f)
        print(progress)


def open_url_F(name):
    headers = {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q='
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
    num = soup.select('body > div.main-content > div.alteration-detail > div.row.header > div.small-12.medium-9.column'
                      's > div:nth-child(1) > div > p > a')[0].text
    print(soup.select('body > div.main-content > div.alteration-detail > div.row.header > div.small-12.medium-9.column'
                      's > div:nth-child(2) > div > p:nth-child({})'.format(int(num) + 1))[0].text.strip())


def open_url_T_1(headers, name, url='https://www.mycancergenome.org/content/alteration/{}/'):
    response = requests.get(url.format(name.replace(' ', '-').lower()), headers=headers)
    if response.status_code == 200:
        data = []
        data.append(name)
        html = response.content.decode(response.encoding)
        soup = BeautifulSoup(html, 'lxml')
        info = soup.select('div#therapies-toggle > p')
        content = ''
        for i in info:
            content += i.text.strip()
        data.append(content)
        num = soup.select('div#therapies-toggle > p:last-of-type > a')[0].text
        reference = soup.select('div.small-12.columns > p.reference')[int(num) - 1].text.strip()
        data.append(reference)
        BDT = soup.select('div#therapies-toggle > div.about-alteration-therapy-row')
        for i in BDT:
            title = i.select('p.about-alteration-therapy-header')[0].text.replace('+', '').strip()
            if title == 'Bosutinib' or title == 'Imatinib':
                Bosutinib = i.select('div.about-alteration-therapy-disease-row')
                for j in Bosutinib:
                    cache = []
                    t1 = j.select('p.about-alteration-therapy-disease-header')[0].text.replace('-', '').strip()
                    cache.append({t1: ''})
                    t2 = \
                    j.select('div.row.table-row.targeted-therapy-table-small-screen-container > div:first-of-type')[
                        0].text
                    data[-1]['info'][title][t1] = t2
                    row = j.select('div.small-12.columns.response-setting-note > div.row')
                    t3 = []
                    for x in row:
                        t3.append(x.text.strip())
                    data[-1]['info'][title][t1][t2] = '%s' % '|'.join(t3)
            else:
                continue
    else:
        return None
    print(data)


def open_url_T_2(headers, name, url='https://www.mycancergenome.org/content/gene/{}/'):
    response = requests.get(url.format(name), headers=headers)
    html = response.content.decode(response.encoding)
    soup = BeautifulSoup(html, 'lxml')
    info = soup.select('div#therapies-toggle > p')
    print(soup)
    content = ''
    for i in info:
        content += i.text.strip()
    print(content)
    num = soup.select('div#therapies-toggle > p:last-of-type > a')[0].text
    reference = soup.select('div.small-12.columns > p.reference')[int(num) - 1].text.strip()
    print(reference)
    BDT = soup.select('div.about-gene-therapy-row')
    print(BDT)
    # for i in BDT:
    #     print(i.select('p.about-gene-therapy-header'))


def main():
    headers = {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q'
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
    hits = 16380
    # get_data(hits)
    # get_info()
    i = 'ABL1'
    i = 'ABL1 E255K'
    open_url_T_1(headers, i)
    # open_url_T_2(headers, i)


if __name__ == '__main__':
    main()
