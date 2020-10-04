import requests


def get_html(url):
    response = requests.get(url)
    return response.content.decode('utf-8')


def main():
    """
    真实网址：https://spa2.scrape.center/
    电影数据网站，无反爬，数据通过 Ajax 加载，数据接口参数加密且有时间限制
    适合动态页面渲染爬取或 JavaScript 逆向分析。
    分析 Ajax 请求，通过 Ajax 请求直接获取 json 格式的网页数据
    下面的 url 是分析 Ajax 请求后得到的网络地址
    offset 参数代表页数，规律是：offset = (页数 - 1) * 10
    token 参数为加密参数
    下面地址代表获取第十页的网页数据
    """
    url = 'https://spa2.scrape.center/api/movie/?limit=10&offset=90&token={}'
    html = get_html(url)
    print(html)


if __name__ == '__main__':
    main()
