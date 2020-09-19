import requests
import time
import random
import re
import xlwt
import json


def get_html(url, cookie):
    header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrom'
                            'e/85.0.4183.83 Safari/537.36',
              'cookie': cookie
              }
    html = requests.get(url=url, headers=header)
    html = html.content.decode('utf-8')
    return html


def deal_data(html):
    find = re.compile(r'g_page_config = \{(.*)\};')
    data = re.findall(find, html)
    file = json.loads('{' + data[0] + '}')
    data = []
    for i in range(44):
        cache = []
        cache.append(file['mods']['itemlist']['data']['auctions'][i]['raw_title'])
        cache.append(file['mods']['itemlist']['data']['auctions'][i]['view_price'])
        cache.append(file['mods']['itemlist']['data']['auctions'][i]['item_loc'])
        try:
            cache.append(file['mods']['itemlist']['data']['auctions'][i]['view_sales'])
        except:
            cache.append(None)
        cache.append(file['mods']['itemlist']['data']['auctions'][i]['nick'])
        data.append(cache)
    return data


def savexlsx(datalist):
    book = xlwt.Workbook(encoding='utf-8')
    sheet = book.add_sheet('爬取结果', cell_overwrite_ok=True)
    tap = ('描述', '价格', '发货地', '销量', '店铺')
    for i in range(0, 5):
        sheet.write(0, i, tap[i])
    for i in range(len(datalist)):
        tap = datalist[i]
        for j in range(0, 5):
            data_1 = tap[j]
            sheet.write(i + 1, j, data_1)
    book.save('淘宝爬虫结果.xlsx')
    print('文件已保存')


def main():
    url = 'https://s.taobao.com/search?q={}&s={}'
    key = str(input('爬取关键字：'))
    page = int(input('爬取页数：'))
    cookie = str(input('粘贴cookie到此处：'))
    datalist = []
    for i in range(page):
        data = get_html(url.format(key, page * 44), cookie)
        data = deal_data(data)
        for j in range(len(data)):
            datalist.append(data[j])
        time.sleep(random.randrange(3, 7, 1))
    savexlsx(datalist)


if __name__ == '__main__':
    main()
