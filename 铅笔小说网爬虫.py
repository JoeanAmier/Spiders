from requests_html import HTMLSession
import re
import os
import unicodedata
import time
import random
from termcolor import colored


def input_data():
    url = input('输入网址：')
    check_url = re.compile(r'^https://www.x23qb.com/book/.*?/')
    url = re.findall(check_url, url)
    if bool(url):
        return url
    else:
        raise ValueError('网址输入错误')


def open_url(url):
    session = HTMLSession()
    if len(url) == 1:
        response = session.get(url[0])
        return response
    elif len(url) > 1:
        html = []
        for page in url:
            response = session.get(page)
            print('获取小说内容中...')
            time.sleep(random.randrange(2, 5, 1))
            html.append(response)
        return html
    else:
        raise TypeError('传入网址发生异常')


def get_url(html):
    title = []
    url = []
    for page in html.html.find('#chapterList li > a'):
        url.append('https://www.x23qb.com' + page.attrs['href'])
        title.append(unicodedata.normalize('NFKC', page.text))
    return title, url


def get_text(text):
    findtext = re.compile(r'chapter\(\);(.*?)铅笔小说', flags=re.DOTALL)
    data = []
    for page in text:
        content = page.html.find('#TextContent')
        if len(content) == 1:
            read = re.findall(findtext, content[0].text)
            if len(read) == 1:
                data.append(read[0])
            else:
                raise ValueError(read)
        else:
            raise ValueError(content)
    return data


def save_txt(book, title, text):
    if len(title) == len(text):
        for index in range(len(title)):
            root = os.getcwd() + '\\' + book + '\\'
            file = root + title[index] + '.txt'
            if not os.path.exists(root):
                os.mkdir(root)
            if not os.path.exists(file):
                with open(file, 'w+', encoding='utf-8') as txt:
                    txt.write(unicodedata.normalize('NFKC', text[index]))
                    txt.close()
                print(colored(title[index] + '保存成功', 'yellow'))
            else:
                save = input(
                    colored(
                        title[index] +
                        '已存在，是否覆盖保存？\n覆盖保存直接回车，不保存请输入任意字符后回车\n需要关闭文件后再覆盖保存\n',
                        'red'))
                if bool(save):
                    print(colored(title[index] + '已存在，未保存', 'red'))
                else:
                    with open(file, 'w+', encoding='utf-8') as txt:
                        txt.write(unicodedata.normalize('NFKC', text[index]))
                        txt.close()
                    print(colored(title[index] + '覆盖保存成功', 'yellow'))
    else:
        print('获取小说数据异常')


def book_root(name):
    name = name.replace('\\', '')
    name = name.replace('/', '')
    name = name.replace('?', '')
    name = name.replace(':', '')
    name = name.replace('*', '')
    name = name.replace('|', '')
    name = name.replace('<', '')
    name = name.replace('>', '')
    name = name.replace('"', '')
    return name


def main():
    url = input_data()
    start = time.time()
    html = open_url(url)
    book = html.html.find('.d_title h1')[0].text
    book = book_root(book)
    title, url = get_url(html)
    html = open_url(url)
    text = get_text(html)
    save_txt(book, title, text)
    print('爬取结束，运行时间：{:.6f}'.format(time.time() - start))


if __name__ == '__main__':
    main()
