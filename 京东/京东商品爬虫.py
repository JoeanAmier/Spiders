from bs4 import BeautifulSoup
import re
from pyppeteer.launcher import launch
import asyncio
import time
import random
from fake_useragent import FakeUserAgent


def get_url(keyword, pages):
    url_list = []
    while pages >= 1 and pages <= 100:
        if pages == 1:
            url = 'https://search.jd.com/Search?keyword={}'.format(
                keyword)
        else:
            url = 'https://search.jd.com/Search?keyword={}&page={}'.format(
                keyword, pages * 2 - 1)
        pages -= 1
        url_list.append(url)
    if len(url_list) != 0:
        url_list.reverse()
        return url_list
    else:
        raise ValueError('页数输入错误')


def deal_data(html):
    soup = BeautifulSoup(html, 'lxml')
    for item in soup.select('ul.gl-warp.clearfix > li.gl-item'):
        print(item.select('div.p-price > strong > i')[0].text)
        print(item.select('div.p-name.p-name-type-2 > a > em')[0].text)
        print(item.select('div.p-commit > strong > a')[0].text)
        print(item.select('div.p-shop > span > a')[0].text)
        for i in item.select('div.p-icons > i'):
            print(i.text)


async def get_html_test(url):
    browser = await launch()
    page = await browser.newPage()
    await page.setUserAgent(FakeUserAgent().chrome)
    await page.evaluateOnNewDocument('Object.defineProperty(navigator, "webdriver", {get: () => undefined})')
    htmls = ''
    for i in url:
        await page.goto(i)
        await page.waitFor(random.randrange(2, 5, 1))
        for j in range(12):
            await page.keyboard.press('PageDown')
            time.sleep(random.randrange(1, 4, 1))
        htmls += await page.content()
    await browser.close()
    return htmls


def main():
    kw = input('搜索关键字：')
    pages = int(input('爬取页数：'))
    html = get_url(kw, pages)
    data = asyncio.get_event_loop().run_until_complete(get_html_test(html))
    deal_data(data)


if __name__ == '__main__':
    """使用无头浏览器爬取"""
    main()
