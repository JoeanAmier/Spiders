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
            pages -= 1
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
    findprice = re.compile(r'<em>￥</em><i>(.*?)</i>')
    findinfo0 = re.compile(r'(.*?)<font class=".*?">(.*?)</font>(.*?)')
    findinfo00 = re.compile(
        r'(.*?)<font class=".*?">(.*?)</font>(.*?)<font class=".*?">(.*?)</font>(.*?)')
    findinfo1 = re.compile(
        r'<em>(.*?)<font class=".*?">(.*?)</font>(.*?)</em>')
    findinfo2 = re.compile(r'<em>(.*?)</em>\n<i class=".*?" id=".*?">.*?</i>')
    findinfo3 = re.compile(
        r'<em><span class=".*?" style=".*?">.*?</span>.*?\n(.*?)<font class=".*?">(.*?)</font></em>')
    findinfo4 = re.compile(
        r'<font class=".*?">(.*?)</font>(.*?)<font class=".*?">(.*?)</font>(.*?)<font class=".*?">(.*?)</font>(.*?)<font class=".*?">(.*?)</font>(.*?)</em>')
    findinfo5 = re.compile(
        r'<font class=".*?">(.*?)</font>(.*?)<font class=".*?">(.*?)</font>(.*?)<font class=".*?">(.*?)</font>(.*?)</em>')
    findinfo6 = re.compile(
        r'<font class=".*?">(.*?)</font>(.*?)<font class=".*?">(.*?)</font>(.*?)</em>')
    findinfo7 = re.compile(r'<font class=".*?">(.*?)</font>(.*?)')
    findinfo8 = re.compile(
        r'<em><span class=".*?" style=".*?">.*?</span>.*?\n(.*?)</em>')
    findstore = re.compile(
        r'<span class=".*?"><a class=".*?" href=".*?" onclick=".*?" target="_blank" title=".*?">(.*?)</a>')
    findgoods = re.compile(r'<i.*?data-tips="京东自营，品质保障">自营</i>')
    data_list = []
    data = BeautifulSoup(html, 'html.parser')
    i = 1
    for item in data.findAll('li', class_='gl-item'):

        cache = []
        item = str(item)
        price = re.findall(findprice, item)
        if len(price) == 1:
            cache.append(price[0])
        else:
            print(item)
            print(price)
            print('第' + str(i) + '条数据价格异常')
            raise ValueError
        info = re.findall(findinfo1, item)
        if bool(info):
            if len(info[0]) == 3:
                info = '%s' % ''.join(list(info[0]))
                cache.append(info)
            else:
                print(item)
                print(info)
                print('第' + str(i) + '条数据描述异常')
                raise ValueError
        else:
            info = re.findall(findinfo2, item)
            if bool(info):
                if len(info) == 1:
                    info = info[0]
                    cache.append(info)
                else:
                    print(item)
                    print(info)
                    print('第' + str(i) + '条数据描述异常')
                    raise ValueError
            else:
                info = re.findall(findinfo3, item)
                if bool(info):
                    if len(info[0]) == 2:
                        info = '%s' % ''.join(list(info[0]))
                        cache.append(info)
                    else:
                        print(item)
                        print(info)
                        print('第' + str(i) + '条数据描述异常')
                        raise ValueError
                else:
                    info = re.findall(findinfo4, item)
                    if bool(info):
                        if len(info[0]) == 8:
                            info = '%s' % ''.join(list(info[0]))
                            cache.append(info)
                        else:
                            print(item)
                            print(info)
                            print('第' + str(i) + '条数据描述异常')
                            raise ValueError
                    else:
                        info = re.findall(findinfo5, item)
                        if bool(info):
                            if len(info[0]) == 6:
                                info = '%s' % ''.join(list(info[0]))
                                cache.append(info)
                            else:
                                print(item)
                                print(info)
                                print('第' + str(i) + '条数据描述异常')
                                raise ValueError
                        else:
                            info = re.findall(findinfo6, item)
                            if bool(info):
                                if len(info[0]) == 4:
                                    info = '%s' % ''.join(list(info[0]))
                                    cache.append(info)
                                else:
                                    print(item)
                                    print(info)
                                    print('第' + str(i) + '条数据描述异常')
                                    raise ValueError
                            else:
                                info = re.findall(findinfo7, item)
                                if bool(info):
                                    if len(info[0]) == 2:
                                        info = '%s' % ''.join(list(info[0]))
                                        cache.append(info)
                                    else:
                                        print(item)
                                        print(info)
                                        print('第' + str(i) + '条数据描述异常')
                                        raise ValueError
                                else:
                                    info = re.findall(findinfo8, item)
                                    if bool(info):
                                        if len(info) == 1:
                                            info = info[0]
                                            cache.append(info)
                                        else:
                                            print(item)
                                            print(info)
                                            print('第' + str(i) + '条数据描述异常')
                                            raise ValueError
                                    else:
                                        print(item)
                                        print(info)
                                        print('第' + str(i) + '条数据描述异常')
                                        raise ValueError
        info_test = re.findall(findinfo00, info)
        if bool(info_test):
            if len(info_test) != 1:
                info_cache = ''
                for j in range(len(info_test)):
                    info_cache += '%s' % ''.join(list(info_test[j]))
                cache[1] = info_cache
            else:
                info = '%s' % ''.join(list(info_test[0]))
                cache[1] = info
        else:
            info = re.findall(findinfo0, info)
            if bool(info):
                info = '%s' % ''.join(list(info[0]))
                cache[1] = info
            else:
                pass
        cache[1] = cache[1].replace('\xa0', ' ')
        store = re.findall(findstore, item)
        if len(store) == 1:
            cache.append(store[0])
        else:
            cache.append(None)
            print('第' + str(i) + '条数据店铺异常')
        if bool(re.findall(findgoods, item)):
            cache.append('自营')
        else:
            cache.append('非自营')
        i += 1
        data_list.append(cache)
    for i in data_list:
        print(i)


async def get_html_test(url):
    browser = await launch()
    page = await browser.newPage()
    await page.setUserAgent(FakeUserAgent().chrome)
    await page.evaluate('''() =>{
        Object.defineProperties(navigator,{ webdriver:{ get: () => false } });
        window.navigator.chrome = { runtime: {},  };
        Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
        Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5,6], });
        }''')
    htmls = ''
    for i in url:
        await page.goto(i)
        await page.waitFor(2500)
        for j in range(12):
            await page.keyboard.press('PageDown')
            time.sleep(random.randrange(1, 5, 1))
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
    main()
