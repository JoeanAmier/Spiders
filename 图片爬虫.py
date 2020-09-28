from pyppeteer import launch
import asyncio
import os
from bs4 import BeautifulSoup
import re
import xlwt
import requests
import time
import random


async def get_html(url, num):
    img = re.compile(r'<img alt="(.*)" data-original="(.*)" data-realurl="')
    data = []
    # 启动浏览器
    browser = await launch({'headless': True, 'args': ['--disable-infobars']})
    page = await browser.newPage()  # 新建页面
    await page.setViewport({'width': 1920, 'height': 1080})  # 设置窗口大小
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/8'
                            '4.0.4147.105 Safari/537.36 Edg/84.0.522.50')
    await page.evaluateOnNewDocument(
        '''() => { Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) }''')
    await page.goto(url)  # 访问网站
    await page.waitFor(2000)
    count = num // 10
    while count != 0:
        await page.keyboard.press('PageDown')
        await page.waitFor(3500)
        count -= 1
    html = await page.content()
    soup = BeautifulSoup(html, 'html.parser')
    for item in soup.find_all('div', class_='Hhalf oneImg'):
        item = str(item)
        # print(item)
        cache = []
        image = re.findall(img, item)
        cache.append(image[0][0])
        cache.append(image[0][1])
        data.append(cache)
    await browser.close()  # 关闭浏览器
    return data


def sava_xlsx(data):
    book = xlwt.Workbook(encoding='utf-8')
    sheet = book.add_sheet('爬取结果', cell_overwrite_ok=True)
    tap = ('关键字', '图片链接')
    for i in range(0, 2):
        sheet.write(0, i, tap[i])  # 添加列标签
    for i in range(len(data)):
        tap = data[i]
        if len(data) >= 100:
            print('\r', end='')
            print('正在保存数据到表格: {:.2f}%'.format(
                ((i + 1) / len(data)) * 100), '▉' * ((i + 1) // (len(data) // 50)), end='')
        elif len(data) < 100 and len(data) > 0:
            print('\r', end='')
            print('正在保存数据到表格: {:.2f}%'.format(
                ((i + 1) / len(data)) * 100), '▉' * ((i + 1) * 50 // (len(data))), end='')
        else:
            print('出现错误')
        for j in range(0, 2):
            data_1 = tap[j]
            sheet.write(i + 1, j, data_1)
    book.save('图片爬虫.xlsx')
    print('\n')


def sava_path(data):
    root = os.getcwd() + '\\爬取结果\\'
    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/8'
        '4.0.4147.105 Safari/537.36 Edg/84.0.522.50'}
    repeat = 0
    for index, item in enumerate(data):
        url = str(item[1])
        path = root + url.split('/')[-1]
        if len(data) >= 100:
            print('\r', end='')
            print('正在下载图片: {:.2f}%'.format(((index + 1) / len(data)) * 100),
                  '▉' * ((index + 1) // (len(data) // 50)),
                  end='')
        else:
            print('\r', end='')
            print('正在下载图片: {:.2f}%'.format(((index + 1) / len(data)) * 100),
                  '▉' * ((index + 1) * 50 // (len(data))),
                  end='')
        try:
            if not os.path.exists(root):  # 判断根目录是否存在
                os.mkdir(root)  # 创建根目录
            if not os.path.exists(path):  # 判断文件是否存在
                file = requests.get(url=url, headers=header)  # 请求文件
                time.sleep(random.randrange(2, 5, 1))
                with open(path, 'wb') as save:
                    save.write(file.content)
                    save.close()
            else:
                repeat += 1
        except BaseException:
            print('')
            print('保存失败')
    print('')
    print('重复图片：' + str(repeat) + '张')


if __name__ == '__main__':
    url = 'https://tu.gxnas.com/'
    print('爬取数量非准确数量')
    num = int(input('爬取数量：'))
    data = asyncio.get_event_loop().run_until_complete(get_html(url, num))
    sava_xlsx(data)
    sava_path(data)
    print('程序结束')
