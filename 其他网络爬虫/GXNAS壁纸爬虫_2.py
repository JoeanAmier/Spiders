import time

import requests

headers = {
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9',
    'dnt': '1',
    'referer': 'https://tu.gxnas.com/',
    'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/'
                  '89.0.4389.90 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest'}


def get_data(url, num):
    data = {
        'cid': '360new',
        'start': num,
        'count': '10'
    }
    response = requests.get(url, headers=headers, params=data)
    print(response.json())


def main(url, num):
    for i in range(num):
        time.sleep(2)
        get_data(url, i)


if __name__ == '__main__':
    page = int(input('爬取页数：'))
    main('https://tu.gxnas.com/api.php', page)
    print('程序结束')
