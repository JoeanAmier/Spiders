import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import time


def get_html(url):
    cookie = {}
    if not cookie:
        return 0
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.43'
                      '89.90 Safari/537.36'}
    response = requests.get(url, headers=headers, cookies=cookie)
    soup = BeautifulSoup(response.text, 'lxml')
    num = [int(i.text.replace("'", '').strip())
           for i in soup.findAll('div', class_="col-md-1")]
    return sum(num)


def main():
    base = 'http://glidedsky.com/level/web/crawler-basic-2?page={}'
    url = [base.format(i) for i in range(1, 1001)]
    start = time.time()
    pool = ThreadPoolExecutor(max_workers=10)
    nums = sum(pool.map(get_html, url))
    print(nums)
    print('爬取用时：{:.6f}'.format(time.time() - start))


if __name__ == '__main__':
    main()
