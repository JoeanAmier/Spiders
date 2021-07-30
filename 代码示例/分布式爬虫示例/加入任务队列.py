import parsel
import requests
from fake_useragent import FakeUserAgent
from redis import Redis


def push_redis_list(text):
    redis = Redis(host='127.0.0.1', port=6379, password='')
    for item in text:
        redis.lpush('标题', item)


def get_url():
    header = {'user-agent': FakeUserAgent().chrome}
    response = requests.get('https://www.baidu.com/', headers=header)
    code = response.encoding
    html = parsel.Selector(text=response.content.decode(code))
    return [
        item
        for item in html.xpath(
            '//ul[@class="s-hotsearch-content"]/li/a/span[2]'
        )
            .css('::text')
            .getall()
    ]


if __name__ == '__main__':
    push_redis_list(get_url())
