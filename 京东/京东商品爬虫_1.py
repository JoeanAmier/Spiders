from bs4 import BeautifulSoup
from pyppeteer.launcher import launch
import asyncio
import time
import random
from fake_useragent import FakeUserAgent
import csv


def get_url(keyword, pages):
    url_list = []
    while 1 <= pages <= 100:
        if pages == 1:
            url = 'https://search.jd.com/Search?keyword={}'.format(
                keyword)
        else:
            url = 'https://search.jd.com/Search?keyword={}&page={}'.format(
                keyword, pages * 2 - 1)
        pages -= 1
        url_list.append(url)
    if not url_list:
        raise ValueError('页数输入错误')
    url_list.reverse()
    return url_list


def deal_data(html):
    soup = BeautifulSoup(html, 'lxml')
    data = []
    for item in soup.select('ul.gl-warp.clearfix > li.gl-item'):
        _ = []
        cache = item.select('div.p-price > strong > i')
        price = cache[0].text.strip() if cache else None
        cache = item.select('div.p-name.p-name-type-2 > a')
        link = 'https:' + cache[0]['href'] if cache else None
        cache = item.select('div.p-name.p-name-type-2 > a > em')
        if cache and len(cache[0].text) <= 4:
            cache = item.select('div.p-name.p-name-type-2 > a > i')
        describe = cache[0].text.replace('\n', '').strip() if cache else None
        cache = item.select('div.p-commit > strong > a')
        evaluate = cache[0].text.strip() if cache else None
        cache = item.select('div.p-shop > span > a')
        shop_name = cache[0].text.strip() if cache else None
        cache = item.select('div.p-icons > i')
        label = [i.text.strip() for i in cache] if cache else None
        _.append(link)
        _.append(price)
        _.append(describe)
        _.append(evaluate)
        _.append(shop_name)
        _.append(label)
        data.append(_)
    return data


def save_data(data):
    with open(f'{time.time()}.csv', 'w', encoding='utf-8', newline='') as f:
        f = csv.writer(f, delimiter=',')
        f.writerows(data)


async def get_html(url):
    browser = await launch()
    page = await browser.newPage()
    await page.setUserAgent(FakeUserAgent().chrome)
    await page.evaluateOnNewDocument('Object.defineProperty(navigator, "webdriver", {get: () => undefined})')
    for i in url:
        await page.goto(i)
        await page.waitFor(random.randrange(2, 5, 1))
        for _ in range(12):
            await page.keyboard.press('PageDown')
            time.sleep(random.randrange(1, 4, 1))
        html = await page.content()
        data = deal_data(html)
        save_data(data)
    await browser.close()


def main():
    kw = input('搜索关键字：')
    pages = int(input('爬取页数：'))
    urls = get_url(kw, pages)
    asyncio.get_event_loop().run_until_complete(get_html(urls))


if __name__ == '__main__':
    """使用无头浏览器爬取"""
    main()
