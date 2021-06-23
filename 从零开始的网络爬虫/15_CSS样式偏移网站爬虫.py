import re
import time
from concurrent.futures import ThreadPoolExecutor

import requests
from bs4 import BeautifulSoup


def get_html(url):
    cookie = {}
    if not cookie:
        return 0
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.43'
                      '89.90 Safari/537.36'}
    response = requests.get(url, headers=headers, cookies=cookie)
    soup = BeautifulSoup(response.text, 'lxml')
    page_num = [
        deal_css(i.findAll('div'), response.text)
        for i in soup.findAll('div', class_="col-md-1")
    ]
    return sum(page_num)


def deal_css(div, text):
    real_numbers = ['' for _ in div]
    for i, j in enumerate(div):
        class_ = j.get('class')[0]
        value = j.text
        if re.findall(f'..{class_} {{ opacity:0 }}', text):
            continue
        position = re.findall(f'..{class_} {{ position:relative }}', text)
        left = re.findall(f'..{class_} {{ left:(.*?)em }}', text)
        content = re.findall(f'..{class_}:before {{ content:"(\\d+)" }}', text)
        if content:
            return int(content[0])
        elif position and left:
            real_numbers[i + int(left[0])] = value
        else:
            real_numbers[i] = value
    return int(''.join(real_numbers))


def main():
    base = 'http://glidedsky.com/level/web/crawler-css-puzzle-1?page={}'
    url = [base.format(i) for i in range(1, 1001)]
    start = time.time()
    pool = ThreadPoolExecutor(max_workers=10)
    nums = sum(pool.map(get_html, url))
    print(nums)
    print('爬取用时：{:.6f}'.format(time.time() - start))


if __name__ == '__main__':
    main()
