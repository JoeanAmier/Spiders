from pyppeteer import launch
import asyncio
import time
import random
import re
from bs4 import BeautifulSoup
import xlwt


async def get_html(_url, _pg):
    try:
        browser = await launch()
        page = await browser.newPage()
        await page.evaluate('''() =>{
            Object.defineProperties(navigator,{ webdriver:{ get: () => false } });
            window.navigator.chrome = { runtime: {},  };
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5,6], });
            }''')
        await page.evaluateOnNewDocument('Object.defineProperty(navigator, "webdriver", {get: () => undefined})')
        for pg in range(1, _pg + 1):
            print('正在爬取第 %d 页数据' % pg)
            await page.goto(_url + 'pg%d' % pg)  # 访问网站
            await page.waitFor(random.randrange(2000, 4000, 200))
            html = await page.content()
            data = deal_data(html)
            save_data(data, pg)
    finally:
        await browser.close()  # 关闭浏览器


def deal_data(html):
    soup = BeautifulSoup(html, 'lxml')
    item = soup.select('ul.sellListContent > li > div.info.clear')
    data = []
    for i in item:
        url = i.find('div', class_='title').a['href']
        title = i.select('div.title > a')[0].text.strip()
        flood = [_.text.strip() for _ in i.select('div.flood > div > a')]
        address = i.select('div.address > div')[0].text.strip()
        followInfo = i.select('div.followInfo')[0].text.strip()
        tag = [_.text.strip() for _ in i.select('div.tag > span')]
        info = [_.text.strip() for _ in i.select('div.priceInfo > div')]
        cache = [
            url,
            title,
            '%s' %
            '-'.join(flood),
            address,
            followInfo,
            '%s' %
            ','.join(tag),
            info[0],
            info[1]]
        data.append(cache)
    return data


def save_data(data, pg):
    top = ['链接', '标题', '位置', '详情', '数据', '标签', '总价', '单价']
    excel = xlwt.Workbook(encoding='utf-8')
    sheet = excel.add_sheet('第%s页爬取结果' % pg, cell_overwrite_ok=True)
    for i in range(len(top)):
        sheet.write(0, i, top[i])
    for i in range(len(data)):
        for x, y in enumerate(data[i]):
            sheet.write(i + 1, x, y)
    excel.save('链家二手房爬取结果_%s.xls' % time.time())


if __name__ == '__main__':
    url = input(
        '正确网址示例：https://bj.lianjia.com/ershoufang/dongcheng/\n错误网址示例：https://bj.lianjia.com/ershoufang/\n输入网址：')
    pg = int(input('输入爬取页数（1~100）：'))
    if pg < 1 or pg > 100:
        print('爬取页数输入错误，本次运行只爬取第一页数据')
        pg = 1
    if re.match(r'https://[a-z]*?.lianjia.com/ershoufang/[a-z]*?/$', url):
        asyncio.get_event_loop().run_until_complete(get_html(url, pg))
    else:
        print('网址输入错误')
