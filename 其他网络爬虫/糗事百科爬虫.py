import re

from requests_html import HTMLSession


def get_html(list):
    session = HTMLSession()
    data = []
    have_url = re.compile('查看全文')
    for url in list:
        html = session.get(url)
        all_article = html.html.find('.contentHerf')
        all_maintext = html.html.find('.main-text')
        for item in range(len(all_article)):
            cache = []
            article = all_article[item].text
            cache.append(article)
            if bool(re.findall(have_url, article)):
                cache.append(
                    'https://www.qiushibaike.com' +
                    all_article[item].attrs['href'])
            else:
                cache.append(None)
            try:
                maintext = all_maintext[item].text
                cache.append(maintext)
            except BaseException:
                cache.append('无')
            data.append(cache)
    return data


def deal_text(data):
    modify2 = re.compile(r'\n[0-9]*')
    for i in data:
        for j in range(3):
            if i[j] is not None:
                i[j] = modify2.sub('', i[j])
            if j == 0:
                print('段子：', i[j])
            elif j == 1:
                if i[j] is not None:
                    print('查看全文：', i[j])
            else:
                print('神评：', i[j])
                print('\n')


def url_list(pages):
    url_list = []
    for i in range(pages):
        if i == 0:
            url = 'https://www.qiushibaike.com/text/'
        else:
            url = 'https://www.qiushibaike.com/text/page/' + str(i + 1) + '/'
        url_list.append(url)
    return (url_list)


def input_data():
    try:
        print('爬取范围（ 1 ~ 13 ）')
        pages = int(input('爬取页数：'))
    except BaseException:
        raise ValueError('页数输入错误')
    if pages >= 1 and pages <= 13:
        return pages
    else:
        raise ValueError('页数输入错误')


def main():
    pages = input_data()
    url = url_list(pages)
    data = get_html(url)
    deal_text(data)


if __name__ == '__main__':
    main()
