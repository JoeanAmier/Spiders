from CharacterFilter import clean
from pyppeteer import launch
import asyncio
import re
import time


async def get_html(url):
    """单页爬取"""
    browser = await launch({'headless': True})
    page = await browser.newPage()
    await page.setViewport({'width': 1920, 'height': 1080})
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chro'
                            'me/89.0.4389.90 Safari/537.36')
    await page.evaluateOnNewDocument('''() =>{
        Object.defineProperties(navigator,{ webdriver:{ get: () => false } });
        window.navigator.chrome = { runtime: {},  };
        Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
        Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5,6], });
        }''')
    await page.goto(url)
    title = await page.content()
    title = re.findall(re.compile(r'<title>(.*?)_在线阅读_九九藏书网</title>'), title)
    if not title:
        await browser.close()
        print('出错了')
        return
    title = clean(title[0])
    for _ in range(20):  # 若爬取内容不全，可增加迭代次数
        await page.keyboard.press('End')
        await page.waitFor(500)
    await page.waitFor(3000)
    png = await page.querySelector('div#content')
    await png.screenshot(path=f'{title}.png')
    await browser.close()


def main():
    url = input('输入网址：')
    start = time.time()
    if re.findall(
            re.compile(r'^http://www.99csw.com/book/[0-9]+?/[0-9]+?.htm$'),
            url):
        asyncio.get_event_loop().run_until_complete(get_html(url))
    print('程序运行时间：{:.6f}'.format(time.time() - start))


if __name__ == '__main__':
    """爬取正文并保存为图像"""
    main()
