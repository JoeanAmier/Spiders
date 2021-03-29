from requests_html import HTMLSession
from fake_useragent import FakeUserAgent

DATA = {
    '_token': None,
    'email': '输入登录邮箱',
    'password': '输入登录密码'
}


def get_cookie(session):
    response = session.get('http://glidedsky.com/login')
    token = response.html.find('input[name=_token]')
    if not token:
        raise ValueError
    DATA['_token'] = token[0].attrs['value']
    session.post('http://glidedsky.com/login', data=DATA)
    return session


def get_html(session, url):
    get_cookie(session)
    headers = {
        'user-agent': FakeUserAgent().chrome
    }
    response = session.get(url, headers=headers)
    num = [int(i.text) for i in response.html.find('div.col-md-1')]
    return sum(num)


def main():
    url = 'http://glidedsky.com/level/web/crawler-basic-1'
    session = HTMLSession()
    print(get_html(session, url))


if __name__ == '__main__':
    main()
