import re

import requests
from parsel import Selector


def get_code(url):
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,"
                  "application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "DNT": "1",
        "Host": "www.expreview.com",
        "Pragma": "no-cache",
        "sec-ch-ua": r'\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"96\", \"Microsoft Edge\";v=\"96\"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": r'\"Windows\"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.62 "}
    resource = requests.get(url, headers=headers)
    if resource.status_code == requests.codes.ok:
        return resource.text
    return ""


def selector(code):
    return Selector(text=code)


def get_text(select):
    text = select.xpath("//div[@id='post_body']/p/text()").getall()
    [print(i) for i in text]


def main():
    # url = input('输入文章链接：')
    url = 'https://www.expreview.com/80774.html'
    if re.match(r'https://www.expreview.com/\d+?.html', url):
        code = get_code(url)
        select = selector(code)
        get_text(select)
    else:
        print('文章链接格式错误！')


if __name__ == '__main__':
    main()
