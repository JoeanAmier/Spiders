from requests_html import HTMLSession
from concurrent.futures import ThreadPoolExecutor
import time

DATA = {
    '_token': None,
    'email': '输入登陆邮箱',
    'password': '输入登陆密码'
}


def get_cookie():
    session = HTMLSession()
    response = session.get('http://glidedsky.com/login')
    token = response.html.find('input[name=_token]')
    if not token:
        raise ValueError
    DATA['_token'] = token[0].attrs['value']
    session.post('http://glidedsky.com/login', data=DATA)
    return session


def get_html(url, session):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.43'
                      '89.90 Safari/537.36'}
    response = session.get(url, headers=headers)
    num = [int(i.text.replace("'", '').strip())
           for i in response.html.find('div.col-md-1')]
    return sum(num)


def main():
    base = 'http://glidedsky.com/level/web/crawler-basic-2?page={}'
    url = [base.format(i) for i in range(1, 1001)]
    start = time.time()
    session = get_cookie()
    session = [session for _ in range(1, 1001)]
    pool = ThreadPoolExecutor(max_workers=10)
    nums = sum(pool.map(get_html, url, session))
    print(nums)
    print('爬取用时：{:.6f}'.format(time.time() - start))


if __name__ == '__main__':
    main()
