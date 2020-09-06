from pyppeteer import launch
import asyncio
import os
from bs4 import BeautifulSoup
import re
import xlwt
import requests
import time
import random

img = re.compile(r'<img alt="(.*)" data-original="(.*)" data-realurl="')

async def get_html(url, num):
    data = []
    browser = await launch({'args': ['--disable-infobars']})
    page = await browser.newPage()
    await page.setViewport({'width': 1920, 'height': 1080})
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/8'
                            '4.0.4147.105 Safari/537.36 Edg/84.0.522.50')
    await page.evaluateOnNewDocument('''() => { Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) }''')
    await page.goto(url)
    await page.waitFor(2000)
    count = num // 10
    while count != 0:
        await page.keyboard.press('PageDown')
        await page.waitFor(3000)
        count -= 1
    html = await page.content()
    soup = BeautifulSoup(html, 'html.parser')
    for item in soup.find_all('div', class_='Hhalf oneImg'):
        item = str(item)
        cache = []
        image = re.findall(img, item)
        cache.append(image[0][0])
        cache.append(image[0][1])
        data.append(cache)
    await browser.close()
    return data

def sava_xlsx(data):
    book = xlwt.Workbook(encoding='utf-8')
    sheet = book.add_sheet('爬取结果', cell_overwrite_ok=True)
    tap = ('关键字', '图片链接')
    for i in range(0, 2):
        sheet.write(0, i, tap[i])
    for i in range(len(data)):
        tap = data[i]
        print('正在获取第' + str(i + 1) + '条数据')
        for j in range(0, 2):
            data_1 = tap[j]
            sheet.write(i + 1, j, data_1)
    book.save('图片爬虫结果.xlsx')

def sava_path(data):
    root = os.getcwd() + '\\爬取结果\\'
    header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/8'
                            '4.0.4147.105 Safari/537.36 Edg/84.0.522.50'}
    for index, item in enumerate(data):
        url = str(item[1])
        path = root + url.split('/')[-1]
        try:
            if not os.path.exists(root):
                os.mkdir(root)
            if not os.path.exists(path):
                time.sleep(random.randrange(2, 5, 1))
                file = requests.get(url=url, headers=header)
                with open(path, 'wb') as save:
                    save.write(file.content)
                    save.close()
                    print('第' + str(index + 1) + '张图片保存成功')
            else:
                print('第' + str(index) + '张图片已存在')
        except:
            print('保存失败')

if __name__ == '__main__':
    url = 'https://tu.gxnas.com/'
    print('输入爬取图片数量（非准确数量）')
    print('输入后回车')
    num = int(input('爬取数量：'))
    data = asyncio.get_event_loop().run_until_complete(get_html(url, num))
    sava_xlsx(data)
    sava_path(data)
    print('程序结束')