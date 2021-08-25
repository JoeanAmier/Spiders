import time

import requests
from fake_useragent import FakeUserAgent

ua = [FakeUserAgent().chrome for _ in range(10)]
for i in ua:
    response = requests.get(
        'https://ja3er.com/json',
        headers={
            'User-Agent': i})
    print(response.json())
    time.sleep(1)
