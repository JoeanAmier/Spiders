from requests_html import HTMLSession
from fake_useragent import FakeUserAgent


def get_html(url):
    headers = {
        'user-agent': FakeUserAgent().chrome
    }
    session = HTMLSession()
    cookie = {}
    if not cookie:
        return '请在代码内输入 cookie 后再爬取'
    response = session.get(url, headers=headers, cookies=cookie)
    num = [int(i.text) for i in response.html.find('div.col-md-1')]
    return sum(num)


def main():
    url = 'http://glidedsky.com/level/web/crawler-basic-1'
    print(get_html(url))


if __name__ == '__main__':
    main()
